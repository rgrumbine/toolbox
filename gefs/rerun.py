''' unet for GEFS sea ice prediction from many atmospheric fields '''

import sys
import os
from math import sin, cos, pi
import datetime

import tracemalloc

import numpy as np
import netCDF4 as nc

import tensorflow as tf
import joblib

#--------------------------------------------------------------
from common import *
from epoch import *
#--------------------------------------------------------------

# ---- These change between target variables and working data --------

# establish variables that depend on what the target is:
nvar    = int(sys.argv[1])  # 0 = icetk, 1 = icec, 2 = sst
nametag = sys.argv[2]       # 'ice' or 'sst', or whatever
final   = sys.argv[3]       # 'sigmoid' for ice, 'linear' for sst and the like

print(nvar, nametag, final, flush=True)
#debug: sys.exit(0)

# Acquire data -- in time range of interest -- RG: argument to be
#Quick:
start  = datetime.datetime(2009,1,6)
end    = datetime.datetime(2010,3,30)
#First decade:
#start = datetime.datetime(2007,1,2)
#end   = datetime.datetime(2016,12,31)
#Second decade:
#start = datetime.datetime(2016,1,5)
#end   = datetime.datetime(2025,12,31)

# ---- From here down should not need to be changed between different runs -----
dt      = datetime.timedelta(1)
nx      = 1536
ny      =  768
nlayer  =   22
ntarget = 1
nlag    = 6
nweeks  = int((end-start)/dt/7 + 1)
print('nweeks = ',nweeks, flush=True)

tracemalloc.start()

Xdata = np.zeros((nweeks, ny, nx, nlayer), dtype=np.float32)
Xavg  = np.zeros((ny, nx, nlayer), dtype=np.float32)
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

# Get, rather than compute, an average field
#getavg.getavg(Xavg, 'thinned/average_1980.nc')
# for climo, move inside loop
atm = climate_trim2007()
ref_date = atm.x[0].epoch

tag   = start
tag  += 7*dt
count = 0
while(tag <= end ):
  print(count, "tag = ",tag, flush = True)
  # for climo:
  for i in range(0, len(atm.x)):
    Xavg[:,:,i] = atm.x[i].climo(tag)
    #debug: print(i,Xavg[:,:,i].max(), Xavg[:,:,i].min(), flush=True )

  flx = nc.Dataset('thinned/week2.'+tag.strftime("%Y%m%d")+'.nc')
  Xdata[count,:,:,0] = flx.variables['ICEC'][:,:]
  Xdata[count,:,:,1] = flx.variables['SST'][:,:]
  Xdata[count,:,:,2] = flx.variables['TMPs'][:,:]
  Xdata[count,:,:,3] = flx.variables['TMP2m'][:,:]
  Xdata[count,:,:,4] = flx.variables['SPFH2m'][:,:]
  Xdata[count,:,:,5] = flx.variables['SHTFL'][:,:]
  Xdata[count,:,:,6] = flx.variables['LHTFL'][:,:]
  Xdata[count,:,:,7] = flx.variables['PWAT'][:,:]
  Xdata[count,:,:,8] = flx.variables['LAND'][:,:]
  #seas is 1 over ocean, 0 over land
  seas  = np.ones((ny, nx), dtype=np.float32)
  seas -= Xdata[count,:,:,8]

  Xdata[count,:,:,9] = flx.variables['PRMSL'][:,:]
  Xdata[count,:,:,10] = flx.variables['z200mb'][:,:]
  Xdata[count,:,:,11] = flx.variables['z500mb'][:,:]
  Xdata[count,:,:,12] = flx.variables['z700mb'][:,:]
  Xdata[count,:,:,13] = flx.variables['z850mb'][:,:]

  Xdata[count,:,:,14] = cos(  (tag-ref_date)/dt * 2.*pi/365.2422)
  Xdata[count,:,:,15] = sin(  (tag-ref_date)/dt * 2.*pi/365.2422)
  Xdata[count,:,:,16] = cos(2*(tag-ref_date)/dt * 2.*pi/365.2422)
  Xdata[count,:,:,17] = sin(2*(tag-ref_date)/dt * 2.*pi/365.2422)
  Xdata[count,:,:,18] = cos(3*(tag-ref_date)/dt * 2.*pi/365.2422)
  Xdata[count,:,:,19] = sin(3*(tag-ref_date)/dt * 2.*pi/365.2422)
  Xdata[count,:,:,20] = clat
  Xdata[count,:,:,21] = slat

  # Remove means so as to have anomalies and something more nearly scaled
  Xdata[count] -= Xavg
  for jjj in range(0,nlayer):
    Xdata[count,:,:,jjj] *= seas

  count += 1
  tag += 7*dt

# hard-wire scaling:
r = [1, 20, 36, 25, 2.e-2, 500, 600, 50, 2.e-4,
        5000,  750, 500, 380, 330, 1, 1, 1, 1, 1, 1]

for l in range(0,nlayer):
    Xdata[:,:,:,l] /= r[l]
    xmax = Xdata[:,:,:,l].max()
    xmin = Xdata[:,:,:,l].min()
    print('scaling ',l,Xdata[:,:,:,l].max(), Xdata[:,:,:,l].min(), '  ',
            r[l], r[l]*(xmax-xmin)/2., flush=True )

#debug: sys.exit(0)

# Finally, set up the training and validation data
split = int(count*0.8 + 0.5)
print('split, count ',split, count, flush=True)
#debug: exit(0)

# RG: Due to memory limits it would be better to go with not copying the data
Xtrain = np.zeros((split, ny, nx, nlayer),dtype=np.float32)
Xval   = np.zeros((count-split-nlag, ny, nx, nlayer),dtype=np.float32)
ytrain = np.zeros((split, ny, nx, nlag),dtype=np.float32)
yval   = np.zeros((count-split-nlag, ny, nx, nlag),dtype=np.float32)

# Now for training and validation
Xtrain = Xdata[:split]
Xval   = Xdata[split:count-nlag]
for i in range(1,nlag+1):
  ytrain[:,:,:,i-1] = Xdata[i:split+i, :,:, nvar] # icec in next month

for i in range(1,nlag+1):
  yval[:,:,:,i-1]   = Xdata[split+i:count-nlag+i, :,:, nvar]

del Xdata

# Get memory metrics: (current, peak)
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 10**6} Mb")
print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)

#--------------------------------------------------------------------------------
# Unet is in common

#--------------------------------------------------------------------------------
# compile, show, and train the unet -- read in an old one if available
if (os.path.exists(nametag+'rerun.joblib')):
  print("about to load joblib",flush=True)
  unet = joblib.load(nametag+'rerun.joblib')
else:
  print("building the unet model", flush=True)
  unet = build_unet(input_shape=(ny,nx,nlayer), final = final, nchannel=nlag)
  unet.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])

unet.summary() # print the model description

# Get memory metrics: (current, peak)
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 10**6} Mb")
print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)

#debug: exit(0)

early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss',
        patience=15, restore_best_weights=True)

#---------------------------------------------------------------------
# Now ready to iteratively fit the model, plot the next week's prediction, permute evaluate it

for period in range(0, 64):
  history = unet.fit(
    Xtrain, ytrain,
    validation_data=(Xval, yval),
    epochs=4,
    batch_size=16,
    callbacks=[early_stopping]
  )
  # Get memory metrics: (current, peak)
  current, peak = tracemalloc.get_traced_memory()
  print(f"{period:02d} past training memory usage: {current / 10**6} Mb")
  print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)

  # save the unet
  joblib.dump(unet, nametag+f"{period:02d}rerun.joblib")
  # Get memory metrics: (current, peak)
  current, peak = tracemalloc.get_traced_memory()
  print(f"past joblib memory usage: {current / 10**6} Mb")
  print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)

  #debug: sys.exit(0)

#--------------------------------------------------------------------------------
  # Visualize -- scaled fields
  #show6(unet, Xval, yval, nvar, figname=nametag+f"{period:02d}.sample6.png")

#--------------------------------------------------------------------------------
  # permutation evaluation of importance
  print(f"\n\nPeriod {period:02d} importances by information layer")
  permute(unet, Xval, yval, nlayer)

# Get memory metrics: (current, peak)
  current, peak = tracemalloc.get_traced_memory()
  print(f"past permutation memory usage: {current / 10**6} Mb")
  print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)

#---------------------------------------------------------------------
