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
def ice_bounds(x):
    x[x < 0.15] = 0
    x[x > 1.0 ] = 1

def score(x):
    y = x
    bias = y.sum()
    y *= y
    mse = y.sum()
    return (bias, mse)

#--------------------------------------------------------------


tstart = time.time()

dt      = datetime.timedelta(1)
nx      = 1536
ny      =  768
nlayer  =   20
nlead   =    6

# for climatology -- epoch has the class
atm = climate_trim()
#debug: print("atm.epoch ",atm.x[0].epoch, flush = True)
start = atm.x[0].epoch

#--------------------------------------------------------------------------------
# read in the unet model
print("\n\n\n")
print("\n\n\n")
print("About to try to load the joblib", flush=True)
if (os.path.exists(sys.argv[1])):
#    try:
        unet = joblib.load(sys.argv[1])
#    except:
#        print("failed to load the unet model, aborting", flush=True)
#        sys.exit(1)
else:
  print("could not find the unet model, aborting", flush=True)
  sys.exit(1)


dtype  = np.float32
Xavg   = np.zeros((ny, nx, nlayer), dtype=np.float32)
Xdata  = np.zeros((1, ny, nx, nlayer), dtype=np.float32)

#tag   = datetime.datetime(1994,1,4)
tag   = datetime.datetime(2026,8,25)
while (tag < datetime.datetime(2026,9,1)):

  # RG: change to enumerate
  for i,item in enumerate(atm.x):
    Xavg[:,:,i] = item.climo(tag)
  #for i in range(0, len(atm.x)):
  #    Xavg[:,:,i] = atm.x[i].climo(tag)
  
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

  for week in range(1, nlead+1):
    tagp = tag + week*dt*7
    
    # write out to netcdf
    out = nc.Dataset("fcst_"+tagp.strftime("%Y%m%d"), "w")
    out.createDimension('ny',ny)
    out.createDimension('nx',nx)
    out.createVariable('ICEC', dtype , ('ny', 'nx'))
    Xout = Xpred[0,:,:,week-1].squeeze()
    out.variables['ICEC'][:,:] = Xout[:,:]
    out.close()

    #--------------------------------------------------

  tag += 7*dt
#--------------------------------------------------------------------
