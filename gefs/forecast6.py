'''
get date of IC / to forecast from
get climatology
compute climatology for date

get IC (will be input netcdf of required files, but for now read in a week):
  find week
  read in for ic
rescale (ic-climo)/scale

get model
make prediction
write out .nc
'''

import sys
import os
from math import sin, cos, pi
import copy
import datetime
import time

import matplotlib.pyplot as plt
#import tracemalloc
import numpy as np
import netCDF4 as nc

#import tensorflow as tf
import joblib
#--------------------------------------------------------------
from epoch import climate_trim
#--------------------------------------------------------------

tstart = time.time()

dt      = datetime.timedelta(1)
nx      = 1536
ny      =  768
nlayer  =   20
nlead   =    6

# Get memory metrics: (current, peak)
Xavg   = np.zeros((ny, nx, nlayer), dtype=np.float32)
Xdata  = np.zeros((1, ny, nx, nlayer), dtype=np.float32)

tag   = datetime.datetime(1994,1,4)

# for climatology -- epoch has the class
atm = climate_trim()
#debug: print("atm.epoch ",atm.x[0].epoch, flush = True)
start = atm.x[0].epoch

for i in range(0, len(atm.x)):
    Xavg[:,:,i] = atm.x[i].climo(tag)

tmp = time.time()
print('time after computing climatology ', tmp-tstart, flush=True)

# RG: In general this will be the GDAS file
flx = nc.Dataset('thinned/week2.'+tag.strftime("%Y%m%d")+'.nc')
Xdata[0,:,:,0] = flx.variables['ICEC'][:,:]
Xdata[0,:,:,1] = flx.variables['SST'][:,:]
Xdata[0,:,:,2] = flx.variables['TMPs'][:,:]
Xdata[0,:,:,3] = flx.variables['TMP2m'][:,:]
Xdata[0,:,:,4] = flx.variables['SPFH2m'][:,:]
Xdata[0,:,:,5] = flx.variables['SHTFL'][:,:]
Xdata[0,:,:,6] = flx.variables['LHTFL'][:,:]
Xdata[0,:,:,7] = flx.variables['PWAT'][:,:]
Xdata[0,:,:,8] = flx.variables['LAND'][:,:]
land = Xdata[0,:,:,8].squeeze()
seas = copy.deepcopy(land)
seas -= 1
seas[seas == -1] = 1
#debug: print("land ",land.max(), land.min() )
#debug: print("seas ",seas.max(), seas.min() )

Xdata[0,:,:,9] = flx.variables['PRMSL'][:,:]
Xdata[0,:,:,10] = flx.variables['z200mb'][:,:]
Xdata[0,:,:,11] = flx.variables['z500mb'][:,:]
Xdata[0,:,:,12] = flx.variables['z700mb'][:,:]
Xdata[0,:,:,13] = flx.variables['z850mb'][:,:]
flx.close()

# RG: Note that start is the epoch for forecasting, 19940101
Xdata[0,:,:,14] = cos(  (tag-start)/dt * 2.*pi/365.2422)
Xdata[0,:,:,15] = sin(  (tag-start)/dt * 2.*pi/365.2422)
Xdata[0,:,:,16] = cos(2*(tag-start)/dt * 2.*pi/365.2422)
Xdata[0,:,:,17] = sin(2*(tag-start)/dt * 2.*pi/365.2422)
Xdata[0,:,:,18] = cos(3*(tag-start)/dt * 2.*pi/365.2422)
Xdata[0,:,:,19] = sin(3*(tag-start)/dt * 2.*pi/365.2422)

# Remove climatology so as to have anomalies
Xdata -= Xavg

# hard-wired scaling:
scale =  [1, 20, 36, 25, 2.e-2, 500, 600, 50, 2.e-4,
        5000,  750, 500, 380, 330, 1, 1, 1, 1, 1, 1]
for l in range(0,nlayer):
    Xdata[0,:,:,l] /= scale[l]

#debug: sys.exit(0)

if (seas.max() != 1 or seas.min() != 0):
  print("seas bollixed",seas.max(), seas.min() )
  sys.exit(1)

#--------------------------------------------------------------------------------

# read in the unet model
if (os.path.exists(sys.argv[1])):
  print("about to load joblib",flush=True)
  unet = joblib.load(sys.argv[1])
else:
  print("could not find the unet model, aborting", flush=True)
  sys.exit(1)
#debug: unet.summary() # print the model description


#---------------------------------------------------------------------
# make a forecast
#debug: print("Xdata shape:",Xdata.shape, flush=True)
Xpred = unet.predict(Xdata)
#debug: print("Xpred shape:",Xpred.shape, flush=True)

tmp = time.time()
print('time after making forecast ', tmp-tstart, flush=True)

nvar = int(sys.argv[2])
# unscale
for i in range(0, nlead):
  Xpred[0,:,:,i] *= scale[nvar]
#debug: print("unscaled anomaly ",Xpred.max(), Xpred.min() , flush=True)

anomaly = copy.deepcopy(Xpred)

# add back in the climatology for each week
for i in range(0, nlead):
  Xpred[0,:,:,i] += Xavg[:,:,nvar]
#debug: print("final prediction",Xpred.max(), Xpred.min() , flush=True)
#debug: print("climatology",Xavg[:,:,nvar].max(), Xavg[:,:,nvar].min() , flush=True)

#--------------------------------------------------------------------

def ice_bounds(x):
    x[x < 0.15] = 0
    x[x > 1.0 ] = 1

def score(x):
    y = x
    bias = y.sum()
    y *= y
    mse = y.sum()
    return (bias, mse)


#Unscale and re-add average
persist = Xdata[0,:,:,nvar].squeeze()
persist *= scale[nvar]
persist += Xavg[:,:,nvar]

if (nvar == 0):
  ice_bounds(persist)

for week in range(1, nlead+1):
  tagp = tag + week*dt*7
  #debug: print("tagp = ",tagp, flush=True)

  Xclimo = atm.x[nvar].climo(tagp)
  flx = nc.Dataset('thinned/week2.'+tagp.strftime("%Y%m%d")+'.nc')
  if (nvar == 0):
    Xobs = flx.variables['ICEC'][:,:]
    ice_bounds(Xpred)
    ice_bounds(Xclimo)
    ice_bounds(Xobs)
  elif (nvar == 1):
    Xobs = flx.variables['SST'][:,:]
  else:
    print("nvar out of range ",nvar, flush=True)
    sys.exit(1)
  flx.close()
  #debug: print("xobs ",Xobs.max(), Xobs.min() )


  fig, ax = plt.subplots(1, 3, figsize=(15, 5))

  # climatology
  im0 = ax[0].imshow(Xclimo.squeeze(), cmap='seismic', origin='lower')
  ax[0].set_title("Climatology")
  fig.colorbar(im0, ax=ax[0])

  # prediction
  im1 = ax[1].imshow(Xpred[0,:,:,week-1].squeeze(), cmap='seismic', origin='lower')
  ax[1].set_title("Prediction")
  fig.colorbar(im1, ax=ax[1])

  # observed
  im2 = ax[2].imshow(Xobs.squeeze(), cmap='seismic', origin='lower')
  ax[2].set_title("Observed")
  fig.colorbar(im2, ax=ax[2])

  plt.tight_layout()
  plt.savefig(f'fcst{week:d}.png')
  plt.close()


  fig, ax = plt.subplots(1,2,figsize=(12,5))

  delta_persist = persist - Xobs
  delta_persist *= seas
  im0 = ax[0].imshow(delta_persist, cmap = 'seismic', origin='lower', vmin=-1, vmax = 1)
  ax[0].set_title(tag.strftime("%Y%m%d")+' Persist - obs')
  fig.colorbar(im0, ax=ax[0])

  delta_fcst = Xpred[0,:,:,week-1].squeeze() - Xobs
  delta_fcst *= seas
  im1 = ax[1].imshow(delta_fcst, cmap = 'seismic', origin='lower', vmin=-1, vmax = 1)
  ax[1].set_title(tagp.strftime("%Y%m%d")+' Forecast - obs')
  fig.colorbar(im1, ax=ax[1])

  delta_climo = Xclimo - Xobs
  delta_climo *= seas

  plt.tight_layout()
  plt.savefig(f'delta{week:d}.png')
  plt.close()

  sp = score(delta_persist)
  sfcst = score(delta_fcst)
  sclim = score(delta_climo)
  print(tagp.strftime("%Y%m%d"),week, sp[0], sp[1], '  ', sfcst[0], sfcst[1], '  ', sclim[0], sclim[1])
  #debug: print('    ', week,delta_persist.max(), delta_fcst.max(), delta_climo.max() )

#--------------------------------------------------------------------

# write out .nc of target field
#ncoutput(Xpred)
