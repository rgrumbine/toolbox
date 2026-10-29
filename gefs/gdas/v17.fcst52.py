'''
get date of IC / to forecast from
get climatology
compute climatology for date

get IC (will be input netcdf of required files)
rescale (ic-climo)/scale

get model
make prediction
write out .nc

Robert Grumbine
15 September 2026
'''

import sys
import os
from math import sin, cos, pi
import copy
import datetime
import time

import numpy as np
import netCDF4 as nc

import joblib
#--------------------------------------------------------------
from epoch import climate_verytrim2007
#--------------------------------------------------------------
def ice_bounds(x):
    #debug: print("ice bounds x shape",x.shape)
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
nlayer  =   15
nlead   =   52

# for climatology -- epoch has the class
atm = climate_verytrim2007()
#debug:
print("atm.epoch ",atm.x[0].epoch, flush = True)
start = atm.x[0].epoch

#--------------------------------------------------------------------------------
# read in the unet model
print("About to try to load the joblib", flush=True)
if (os.path.exists(sys.argv[1])):
    try:
        unet = joblib.load(sys.argv[1])
        tmp = time.time()
        print('time after loading joblib ', tmp-tstart, flush=True)
    except:
        print("failed to load the unet model, aborting", flush=True)
        sys.exit(1)
else:
  print("could not find the unet model, aborting", flush=True)
  sys.exit(1)


dtype  = np.float32
Xavg   = np.zeros((ny, nx, nlayer), dtype=np.float32)
Xdata  = np.zeros((1, ny, nx, nlayer), dtype=np.float32)

#tag   = datetime.datetime(2025,9,16)
#tag   = datetime.datetime(2026,5,19)
#tag   = datetime.datetime(2026,9,14)
tag = datetime.datetime.today() - 6*dt 
#while (tag < datetime.datetime(2025,9,21)):
#while (tag < datetime.datetime(2026,5,25)):
while (tag < datetime.datetime.today() ):

  # RG: change to enumerate
  for i,item in enumerate(atm.x):
    Xavg[:,:,i] = item.climo(tag)
  #for i in range(0, len(atm.x)):
  #    Xavg[:,:,i] = atm.x[i].climo(tag)

  tmp = time.time()
  print('time after computing climatology ', tmp-tstart, flush=True)

  # RG: In general this will be the averaged GDAS file
  flx = nc.Dataset('thinned.v17/week2.'+tag.strftime("%Y%m%d")+'.nc')
  Xdata[0,:,:,0] = flx.variables['ICEC'][:,:]
  print("icec ",Xdata[0,:,:,0].max(), Xdata[0,:,:,0].min() )
  
  # Special treatment because replay puts sst everywhere but v17 flags some points
  sstmp = flx.variables['SST'][:,:]
  sstmp[sstmp > 400] = 273.15
  Xdata[0,:,:,1] = sstmp
  print("sst ",Xdata[0,:,:,1].max(), Xdata[0,:,:,1].min() )

  Xdata[0,:,:,2] = flx.variables['TMPs'][:,:]
  print("tmps ",Xdata[0,:,:,2].max(), Xdata[0,:,:,2].min() )
  Xdata[0,:,:,3] = flx.variables['TMP2m'][:,:]
  print("tmp2m ",Xdata[0,:,:,3].max(), Xdata[0,:,:,3].min() )

  #seas is 1 over ocean, 0 over land
  seas = np.ones((ny,nx), dtype=np.float32)
  seas -= flx.variables['LAND'][:,:]
  #Xdata[0,:,:,8] = flx.variables['LAND'][:,:]
  #print("land ",Xdata[0,:,:,8].max(), Xdata[0,:,:,8].min() )

  Xdata[0,:,:,4] = flx.variables['PRMSL'][:,:]
  print("prmsl ",Xdata[0,:,:,4].max(), Xdata[0,:,:,4].min() )
  Xdata[0,:,:,5] = flx.variables['z200mb'][:,:]
  print("z200 ",Xdata[0,:,:,5].max(), Xdata[0,:,:,5].min() )
  Xdata[0,:,:,6] = flx.variables['z500mb'][:,:]
  print("z500 ",Xdata[0,:,:,6].max(), Xdata[0,:,:,6].min() )
  Xdata[0,:,:,7] = flx.variables['z700mb'][:,:]
  print("z700 ",Xdata[0,:,:,7].max(), Xdata[0,:,:,7].min() )
  Xdata[0,:,:,8] = flx.variables['z850mb'][:,:]
  print("z850 ",Xdata[0,:,:,8].max(), Xdata[0,:,:,8].min() )

  flx.close()

  # RG: Note that start is the epoch for forecasting
  Xdata[0,:,:,9] = cos(  (tag-start)/dt * 2.*pi/365.2422)
  Xdata[0,:,:,10] = sin(  (tag-start)/dt * 2.*pi/365.2422)
  Xdata[0,:,:,11] = cos(2*(tag-start)/dt * 2.*pi/365.2422)
  Xdata[0,:,:,12] = sin(2*(tag-start)/dt * 2.*pi/365.2422)
  Xdata[0,:,:,13] = cos(3*(tag-start)/dt * 2.*pi/365.2422)
  Xdata[0,:,:,14] = sin(3*(tag-start)/dt * 2.*pi/365.2422)
  
  # Remove climatology so as to have anomalies
  Xdata -= Xavg
  for jjj in range(0,nlayer):
      Xdata[0,:,:,jjj] *= seas

  # hard-wired scaling:
  scale =  [1, 20, 36, 25,
          5000,  750, 500, 380, 330, 1, 1, 1, 1, 1, 1]
  for l in range(0,nlayer):
      Xdata[0,:,:,l] /= scale[l]

  #debug: sys.exit(0)

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
  # Get the lat-lons
  flx = nc.Dataset('thinned.v17/flx.'+tag.strftime("%Y%m%d")+'.nc')
  lats = flx.variables['latitude'][:]
  lons = flx.variables['longitude'][:]
  flx.close()

  for week in range(1, nlead+1):
    tagp = tag + week*dt*7
    
    # write out to netcdf
    out = nc.Dataset("fcst_"+tagp.strftime("%Y%m%d")+".nc", "w")
    out.createDimension('ny',ny)
    out.createDimension('nx',nx)
    out.createVariable('latitude', dtype, ('ny') )
    out.createVariable('longitude', dtype, ('nx') )
    out.createVariable('ICEC', dtype , ('ny', 'nx'))

    out.variables['latitude'][:]  = lats[:]
    out.variables['longitude'][:] = lons[:]

    Xout = Xpred[0,:,:,week-1].squeeze()
    ice_bounds(Xout)
    out.variables['ICEC'][:,:] = Xout

    out.close()

    #--------------------------------------------------

  tag += 7*dt
#--------------------------------------------------------------------
