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

import tracemalloc
import numpy as np
import netCDF4 as nc

import tensorflow as tf
import joblib
#--------------------------------------------------------------
#from common import *
from epoch import *
#--------------------------------------------------------------

tstart = time.time()

tracemalloc.start()

dt      = datetime.timedelta(1)
nx      = 1536
ny      =  768
nlayer  =   26

# Get memory metrics: (current, peak)
Xavg   = np.zeros((ny, nx, nlayer), dtype=np.float32)
Xdata  = np.zeros((1, ny, nx, nlayer), dtype=np.float32)

tag   = datetime.datetime(1994,1,4)

# for climatology -- epoch has the class
atm = climate2()
#debug: print("atm.epoch ",atm.x[0].epoch, flush = True)
start = atm.x[0].epoch

for i in range(0, len(atm.x)):
    Xavg[:,:,i] = atm.x[i].climo(tag)

tmp = time.time()
print('time after computing climatology ', tmp-tstart)

current, peak = tracemalloc.get_traced_memory()
print(f"Memory usage after apportioning climate: {current / 10**6} Mb")
print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)
#debug: sys.exit(0)

# RG: In general this will be the GDAS file
flx = nc.Dataset('thinned/week2.'+tag.strftime("%Y%m%d")+'.nc')
Xdata[0,:,:,0] = flx.variables['ICETK'][:,:]
Xdata[0,:,:,1] = flx.variables['ICEC'][:,:]
Xdata[0,:,:,2] = flx.variables['SST'][:,:]
Xdata[0,:,:,3] = flx.variables['USWRF'][:,:]
Xdata[0,:,:,4] = flx.variables['TMPs'][:,:]
Xdata[0,:,:,5] = flx.variables['TMP2m'][:,:]
Xdata[0,:,:,6] = flx.variables['SPFH2m'][:,:]
Xdata[0,:,:,7] = flx.variables['U10m'][:,:]
Xdata[0,:,:,8] = flx.variables['V10m'][:,:]
Xdata[0,:,:,9] = flx.variables['SHTFL'][:,:]
Xdata[0,:,:,10] = flx.variables['LHTFL'][:,:]
Xdata[0,:,:,11] = flx.variables['PWAT'][:,:]
Xdata[0,:,:,12] = flx.variables['LAND'][:,:]

Xdata[0,:,:,13] = flx.variables['PRMSL'][:,:]
Xdata[0,:,:,14] = flx.variables['z1mb'][:,:]
Xdata[0,:,:,15] = flx.variables['z10mb'][:,:]
Xdata[0,:,:,16] = flx.variables['z200mb'][:,:]
Xdata[0,:,:,17] = flx.variables['z500mb'][:,:]
Xdata[0,:,:,18] = flx.variables['z700mb'][:,:]
Xdata[0,:,:,19] = flx.variables['z850mb'][:,:]
flx.close()

# RG: Note that start should be epoch for forecasting, 19940101
# RG: note that this should be 365.2422
Xdata[0,:,:,20] = cos( (tag-start)/dt * 2.*pi/365.25)
Xdata[0,:,:,21] = sin( (tag-start)/dt * 2.*pi/365.25)
Xdata[0,:,:,22] = cos(2*(tag-start)/dt * 2.*pi/365.25)
Xdata[0,:,:,23] = sin(2*(tag-start)/dt * 2.*pi/365.25)
Xdata[0,:,:,24] = cos(3*(tag-start)/dt * 2.*pi/365.25)
Xdata[0,:,:,25] = sin(3*(tag-start)/dt * 2.*pi/365.25)

# Remove climatology so as to have anomalies 
Xdata -= Xavg

# hard-wired scaling:
#scale = [15, 1.2, 20, 600, 3800, 3100, 2225,  750, 500, 350, 300, 1, 1, 1, 1, 1, 1]
scale  = [19, 1, 20, 600, 36, 25, 1.5e-2, 10, 10, 500, 500, 45, 2.e-4,
           5000, 3400, 2500,  780, 530, 390, 340, 1, 1, 1, 1, 1, 1 ]  

for l in range(0,nlayer):
    Xdata[0,:,:,l] /= scale[l]


#debug: sys.exit(0)

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

tmp = time.time()
print('time after making forecast ', tmp-tstart)
current, peak = tracemalloc.get_traced_memory()
print(f"After making prediction memory usage: {current / 10**6} Mb")
print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)

#debug: print("Xpred shape:",Xpred.shape, flush=True)
#debug:
print("predicted scaled",Xpred.max(), Xpred.min() , flush=True)
#debug: sys.exit(0)

nvar = int(sys.argv[2])
# unscale
Xpred[0,:,:,0] *= scale[nvar]
#debug:
print("unscaled anomaly ",Xpred.max(), Xpred.min() , flush=True)

# add back in the climatology
anomaly = copy.deepcopy(Xpred)

Xpred[0,:,:,0]+= Xavg[:,:,nvar]
#debug:
print("final prediction",Xpred.max(), Xpred.min() , flush=True)
print("climatology",Xavg[:,:,nvar].max(), Xavg[:,:,nvar].min() , flush=True)

#--------------------------------------------------------------------
# plot climatology, forecast, anomaly
#plot Xavg[nvar]
#plot Xpred
#plot anomaly
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(15, 5))

# climatology
im0 = ax[0].imshow(Xavg[:,:,nvar].squeeze(), cmap='seismic', origin='lower')
ax[0].set_title("Climatology")
fig.colorbar(im0, ax=ax[0])

# prediction
im1 = ax[1].imshow(Xpred[0,:,:,0].squeeze(), cmap='seismic', origin='lower')
ax[1].set_title("Prediction")
fig.colorbar(im1, ax=ax[1])

# anomaly
im2 = ax[2].imshow(anomaly[0,:,:,0].squeeze(), cmap='seismic', origin='lower')
ax[2].set_title("Anomaly")
fig.colorbar(im2, ax=ax[2])

plt.tight_layout()
plt.savefig('fcst.png')
plt.close()

# Solo anomaly field with narrow bounds
fig,ax = plt.subplots(1,1,figsize=(12,6))
im = ax.imshow(anomaly[0,:,:,0].squeeze(), cmap='seismic', origin='lower',
        vmin=-scale[nvar]/5., vmax=scale[nvar]/5.)
ax.set_title('Anomaly')
fig.colorbar(im, ax=ax)
plt.tight_layout()
plt.savefig('anomaly.png')
plt.close()

#--------------------------------------------------------------------


# write out .nc of target field
#ncoutput(Xpred)
