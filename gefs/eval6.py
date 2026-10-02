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
from math import sin, cos, pi, floor
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
from epoch import climate_trim2007
#--------------------------------------------------------------
def ice_bounds(x):
    x[x < 0.15] = 0
    x[x > 1.0 ] = 1

def score(x):
    y = x.copy()
    bias = y.sum()
    y *= y
    sse = y.sum()
    return (bias, sse)

#--------------------------------------------------------------


tstart = time.time()

dt      = datetime.timedelta(1)
nx      = 1536
ny      =  768
nlayer  =   22
nlead   =    6

# for climatology -- epoch has the class
atm = climate_trim2007()
#debug: print("atm.epoch ",atm.x[0].epoch, flush = True)
start = atm.x[0].epoch

#--------------------------------------------------------------------------------
# read in the unet model
if (os.path.exists(sys.argv[1])):
  unet = joblib.load(sys.argv[1])
else:
  print("could not find the unet model, aborting", flush=True)
  sys.exit(1)
#debug: unet.summary() # print the model description
tmp = time.time()
print('time after getting joblib ', tmp-tstart, flush=True)


Xavg   = np.zeros((ny, nx, nlayer), dtype=np.float32)
Xdata  = np.zeros((1, ny, nx, nlayer), dtype=np.float32)
clat  = np.zeros((ny, nx), dtype=np.float32)
slat  = np.zeros((ny, nx), dtype=np.float32)

# to work with latitudes
llfile = nc.Dataset('thinned/flx.19920101.nc','r')
lats = llfile.variables['latitude'][:]
llfile.close()
rads = np.radians(lats)
c = np.cos(rads)
s = np.sin(rads)
#orig
#for j in range(0,ny):
#    clat[j,:] = c
#    slat[j,:] = s
#From gemini:
clat = np.tile(c[:, np.newaxis], (1, nx))
slat = np.tile(s[:, np.newaxis], (1, nx))
print("cos ",clat.max(), clat.min() )
print("sin ",slat.max(), slat.min() )


tag   = datetime.datetime(1994,1,4)
tag   = datetime.datetime(2007,1,2)
tag   = datetime.datetime(2009,1,6)
#while (tag < datetime.datetime(2025,12,31)):
#while (tag < datetime.datetime(2016,12,31)):
while (tag < datetime.datetime(2009,12,31)):

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
  Xdata[0,:,:,20] = clat
  Xdata[0,:,:,21] = slat
  
  # Remove climatology so as to have anomalies for the prediction
  Xdata -= Xavg
  # Seas-only case
  for jjj in range(0, nlayer):
      Xdata[0,:,:,jjj] *= seas

  # hard-wired scaling:
  scale =  [1, 20, 36, 25, 2.e-2, 500, 600, 50, 2.e-4,
          5000,  750, 500, 380, 330, 1, 1, 1, 1, 1, 1, 1, 1]
  for l in range(0,nlayer):
      Xdata[0,:,:,l] /= scale[l]

  if (seas.max() != 1 or seas.min() != 0):
    print("seas bollixed",seas.max(), seas.min() )
    sys.exit(1)

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

  # add back in the climatology for each week
  for i in range(0, nlead):
    Xpred[0,:,:,i] += Xavg[:,:,nvar]
  #debug: print("final prediction",Xpred.max(), Xpred.min() , flush=True)
  #debug: print("climatology",Xavg[:,:,nvar].max(), Xavg[:,:,nvar].min() , flush=True)

  #--------------------------------------------------------------------

  #Unscale and re-add average
  persist = Xdata[0,:,:,nvar].copy() * scale[nvar]
  #persist *= scale[nvar]
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
      ice_bounds(Xpred[0,:,:,week-1])
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
    im0 = ax[0].imshow(Xclimo.squeeze()*seas, cmap='seismic', origin='lower')
    ax[0].set_title("Climatology")
    fig.colorbar(im0, ax=ax[0])

    # prediction
    im1 = ax[1].imshow(Xpred[0,:,:,week-1].squeeze()*seas, cmap='seismic', origin='lower')
    ax[1].set_title("Prediction")
    fig.colorbar(im1, ax=ax[1])

    # observed
    im2 = ax[2].imshow(Xobs.squeeze()*seas, cmap='seismic', origin='lower')
    ax[2].set_title("Observed")
    fig.colorbar(im2, ax=ax[2])

    plt.tight_layout()
    plt.savefig(f'fcst{week:d}_'+tag.strftime("%Y%m%d")+'.gif')
    plt.close()


    fig, ax = plt.subplots(1,3,figsize=(12,5))

    delta_persist = persist - Xobs
    delta_persist *= seas

    delta_fcst = Xpred[0,:,:,week-1].squeeze() - Xobs
    delta_fcst *= seas

    delta_climo = Xclimo - Xobs
    delta_climo *= seas
    
    scale = floor(max(abs(delta_persist.max()),abs(delta_persist.min() ) ))
    scale = max(1, scale)

    im0 = ax[0].imshow(delta_persist, cmap = 'seismic', origin='lower', vmin=-1*scale, vmax = 1*scale)
    ax[0].set_title(tag.strftime("%Y%m%d")+' Persist - obs')
    fig.colorbar(im0, ax=ax[0])

    im1 = ax[1].imshow(delta_fcst, cmap = 'seismic', origin='lower', vmin=-1*scale, vmax = 1*scale)
    ax[1].set_title(tagp.strftime("%Y%m%d")+' Forecast - obs')
    fig.colorbar(im1, ax=ax[1])

    im2 = ax[2].imshow(delta_climo, cmap = 'seismic', origin='lower', vmin=-1*scale, vmax = 1*scale)
    ax[2].set_title(tagp.strftime("%Y%m%d")+' Climatology - obs')
    fig.colorbar(im2, ax=ax[2])

    plt.tight_layout()
    plt.savefig(f'delta{week:d}_'+tag.strftime("%Y%m%d")+'.gif')
    plt.close()

    sp    = score(delta_persist)
    sfcst = score(delta_fcst)
    sclim = score(delta_climo)
    print(tagp.strftime("%Y%m%d"),week, f'{sp[0]:8.1f}, {sp[1]:8.1f}', '  ', 
            f'{sfcst[0]:8.1f}, {sfcst[1]:8.1f}', '  ', f'{sclim[0]:8.1f}, {sclim[1]:8.1f}')
    #debug: print('    ', week,delta_persist.max(), delta_fcst.max(), delta_climo.max() )

  tag += 7*dt
#--------------------------------------------------------------------
