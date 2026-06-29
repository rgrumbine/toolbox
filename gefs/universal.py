''' unet for GEFS sea ice prediction from many atmospheric fields '''

import sys
import os
from math import sin, cos, pi
import datetime
import time

import tracemalloc

import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras import layers, models, Input
import joblib

#--------------------------------------------------------------
import getavg
from common import *
#--------------------------------------------------------------

# ---- These change between target variables and working data --------

# establish variables that depend on what the target is:
#nvar    = 1         # 0 = icetk, 1 = icec, 2 = sst
#nametag = 'ice'     # or 'sst', or whatever
#final   = 'sigmoid' # 'linear' for sst and the like
nvar    = int(sys.argv[1])  # 0 = icetk, 1 = icec, 2 = sst
nametag = sys.argv[2]       # 'ice' or 'sst', or whatever
final   = sys.argv[3]       # 'sigmoid' for ice, 'linear' for sst and the like

print(nvar, nametag, final, flush=True)
#debug: sys.exit(0)

# Acquire data -- in time range of interest
start = datetime.datetime(1980,1,1)
end   = datetime.datetime(1988,3,6)

# ---- From here down should not need to be changed between different runs -----
dt      = datetime.timedelta(1)
nx      = 1536
ny      =  768
nlayer  = 15
ntarget = 1
nlag    = 1
nweeks  = int((end-start)/dt/7 + 1)
print('nweeks = ',nweeks, flush=True)

tracemalloc.start()

Xdata = np.zeros((nweeks, ny, nx, nlayer), dtype=np.float32)
Xavg  = np.zeros((ny, nx, nlayer), dtype=np.float32)
# Get memory metrics: (current, peak)
current, peak = tracemalloc.get_traced_memory()
print(f"Memory usage after np.zeros: {current / 10**6} Mb")
print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)

# Get, rather than compute, an average field
getavg.getavg(Xavg, 'thinned/average_1980.nc')

tag   = start 
tag += 7*dt
count = 0
while(tag <= end ):
  print(count, "tag = ",tag, flush = True)

  flx = nc.Dataset('../thinned/week.'+tag.strftime("%Y%m%d")+'.nc')
  Xdata[count,:,:,0] = flx.variables['ICETK'][:,:]
  Xdata[count,:,:,1] = flx.variables['ICEC'][:,:]
  Xdata[count,:,:,2] = flx.variables['SST'][:,:]
  Xdata[count,:,:,3] = flx.variables['USWRF'][:,:]

  Xdata[count,:,:,4] = flx.variables['PRMSL'][:,:]
  Xdata[count,:,:,5] = flx.variables['z1mb'][:,:]
  Xdata[count,:,:,6] = flx.variables['z10mb'][:,:]
  Xdata[count,:,:,7] = flx.variables['z200mb'][:,:]
  Xdata[count,:,:,8] = flx.variables['z500mb'][:,:]
  Xdata[count,:,:,9] = flx.variables['z700mb'][:,:]
  Xdata[count,:,:,10] = flx.variables['z850mb'][:,:]

  Xdata[count,:,:,11] = cos( (tag-start)/dt * 2.*pi/365.25)
  Xdata[count,:,:,12] = sin( (tag-start)/dt * 2.*pi/365.25)
  Xdata[count,:,:,13] = cos(2*(tag-start)/dt * 2.*pi/365.25)
  Xdata[count,:,:,14] = sin(2*(tag-start)/dt * 2.*pi/365.25)

  # Remove means so as to have anomalies and something more nearly scaled
  Xdata[count] -= Xavg

  count += 1
  tag += 7*dt
  #debug: print("reached end of read", flush=True)
  #debug: exit(0)

# Scale by max-min:
r = np.zeros((nlayer))
for l in range(0,nlayer):
    r[l] = 0.5*(Xdata[:,:,:,l].max() - Xdata[:,:,:,l].min() ) 
    Xdata[:,:,:,l] /= r[l]
    print('scaling ',l,Xdata[:,:,:,l].max(), Xdata[:,:,:,l].min(), '  ', r[l], flush=True )

# Get memory metrics: (current, peak)
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 10**6} Mb")
print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)


# Finally, set up the training and validation data
split = int(count*0.8 + 0.5)
#split = 365
print('split, count ',split, count, flush=True)
#debug: exit(0)

# RG: Due to memory limits it would be better to go with not copying the data
Xtrain = np.zeros((split, ny, nx, nlayer),dtype=np.float32)
ytrain = np.zeros((split, ny, nx, 1),dtype=np.float32)
Xval   = np.zeros((count-split-nlag, ny, nx, nlayer),dtype=np.float32)
yval   = np.zeros((count-split-nlag, ny, nx, 1),dtype=np.float32)

# Now for training and validation
Xtrain = Xdata[:split]
ytrain = Xdata[1:split+1, :,:, nvar] # icec in next month
Xval   = Xdata[split:count-1-nlag]
yval   = Xdata[split+1:count-nlag, :,:, nvar]

del Xdata

# Get memory metrics: (current, peak)
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 10**6} Mb")
print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)

#--------------------------------------------------------------------------------
# Unet is in common
    
#--------------------------------------------------------------------------------
# compile, show, and train the unet -- read in an old one if available
if (os.path.exists(nametag+'week.joblib')):
  print("about to load joblib",flush=True)
  unet = joblib.load(nametag+'week.joblib')
else:
  print("building the unet model", flush=True)
  unet = build_unet(input_shape=(ny,nx,nlayer), final = final)
  unet.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])

unet.summary() # print the model description

# Get memory metrics: (current, peak)
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 10**6} Mb")
print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)

#debug: exit(0)

early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)

#---------------------------------------------------------------------
# Now ready to iteratively fit the model, plot the next week's prediction, permute evaluate it

for period in range(0, 10):
  history = unet.fit(
    Xtrain, ytrain,
    validation_data=(Xval, yval),
    epochs=1,
    batch_size=16,
    callbacks=[early_stopping]
  )
  # Get memory metrics: (current, peak)
  current, peak = tracemalloc.get_traced_memory()
  print(f"{period:02d} past training memory usage: {current / 10**6} Mb")
  print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)

  # save the unet
  joblib.dump(unet, nametag+f"{period:02d}week.joblib")
  # Get memory metrics: (current, peak)
  current, peak = tracemalloc.get_traced_memory()
  print(f"past joblib memory usage: {current / 10**6} Mb")
  print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)
  
  #debug: sys.exit(0)

#--------------------------------------------------------------------------------
  # Visualize:
  show(unet, Xval, yval, figname=nametag+f"{period:02d}.sample.png")

#--------------------------------------------------------------------------------
  # permutation evaluation of importance
  print(f"\n\nPeriod {period:02d} importances by information layer")
  permute(unet, Xval, yval, nlayer)

# Get memory metrics: (current, peak)
  current, peak = tracemalloc.get_traced_memory()
  print(f"past permutation memory usage: {current / 10**6} Mb")
  print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)
