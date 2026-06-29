''' unet for GEFS sea ice prediction from many atmospheric fields '''

from math import sin, cos, pi
import datetime

import numpy as np
import netCDF4 as nc

import joblib

#--------------------------------------------------------------
import getavg
from common import *
#--------------------------------------------------------------

print('done importing libraries',flush=True)

# Acquire basic data -- grids for days/months 1-540
start = datetime.datetime(1980,1,1)
dt    = datetime.timedelta(1)
end   = datetime.datetime(1980,3,31)

nx = 1536
ny =  768
nlayer = 15
ntarget = 1
nlag    = 1
ndays   = int((end-start)/dt + 1)
print('ndays = ',ndays, flush=True)

Xdata = np.zeros((ndays, ny, nx, nlayer), dtype=np.float32)
Xavg  = np.zeros((ny, nx, nlayer), dtype=np.float32)

# Get, rather than compute, an average field
getavg.getavg(Xavg, fname = 'thinned/average_1980.nc')

tag   = start
count = 0
while(tag <= end and count < ndays):
  print(count, "tag = ",tag, flush = True)

  flx = nc.Dataset('flx.'+tag.strftime("%Y%m%d")+'.nc')
  Xdata[count,:,:,0] = flx.variables['ICETK_surface'][0,:,:]
  Xdata[count,:,:,1] = flx.variables['ICEC_surface'][0,:,:]
  Xdata[count,:,:,2] = flx.variables['FDNSSTMP_surface'][0,:,:]
  Xdata[count,:,:,3] = flx.variables['USWRF_surface'][0,:,:]
  flx.close()

  prs = nc.Dataset('prs.'+tag.strftime("%Y%m%d")+'.nc')
  Xdata[count,:,:,4] = prs.variables['PRMSL_meansealevel'][0,:,:]
  Xdata[count,:,:,5] = prs.variables['HGT_1mb'][0,:,:]
  Xdata[count,:,:,6] = prs.variables['HGT_10mb'][0,:,:]
  Xdata[count,:,:,7] = prs.variables['HGT_200mb'][0,:,:]
  Xdata[count,:,:,8] = prs.variables['HGT_500mb'][0,:,:]
  Xdata[count,:,:,9] = prs.variables['HGT_700mb'][0,:,:]
  Xdata[count,:,:,10] = prs.variables['HGT_850mb'][0,:,:]
  prs.close()

  Xdata[count,:,:,11] = cos( (tag-start)/dt * 2.*pi/365.25)
  Xdata[count,:,:,12] = sin( (tag-start)/dt * 2.*pi/365.25)
  Xdata[count,:,:,13] = cos(2*(tag-start)/dt * 2.*pi/365.25)
  Xdata[count,:,:,14] = sin(2*(tag-start)/dt * 2.*pi/365.25)

  # Remove means so as to have anomalies and something more nearly scaled
  Xdata[count] -= Xavg

  count += 1
  tag += dt

# Scale by max-min:
r = np.zeros((nlayer))
for l in range(0,nlayer):
    # Scale by 0.5*(max - min)
    r[l] = 0.5*(Xdata[:,:,:,l].max() - Xdata[:,:,:,l].min() ) 
    Xdata[:,:,:,l] /= r[l]
    print('scaling',l,Xdata[:,:,:,l].max(), Xdata[:,:,:,l].min(), '  ', r[l], flush=True )
# RG: Save average fields and scaling factor so as to be able to run on new data

# Finally, set up the training and validation data
split = int(count*0.8 + 0.5)
print('split, count ',split, count, flush=True)
#debug: exit(0)

# RG: Due to memory limits it would be better to go with not copying the data
Xtrain = np.zeros((split, ny, nx, nlayer),dtype=np.float32)
ytrain = np.zeros((split, ny, nx, 1),dtype=np.float32)
Xval   = np.zeros((count-split-nlag, ny, nx, nlayer),dtype=np.float32)
yval   = np.zeros((count-split-nlag, ny, nx, 1),dtype=np.float32)

nvar = 1 # 0 = icetk, 1 = icec, 2 = sst
Xtrain = Xdata[:split]
ytrain = Xdata[1:split+1, :,:, nvar] # icec in next month
Xval   = Xdata[split:count-1-nlag]
yval   = Xdata[split+1:count-nlag, :,:, nvar]

del Xdata

#--------------------------------------------------------------------------------
# design the Unet 
# -- now in common.py

# compile, show, and train the unet -- read in an old one if available
print("about to load joblib",flush=True)
unet = joblib.load('thinned/sstweek.joblib')

unet.summary() # print the model description

#--------------------------------------------------------------------------------
# Extract a sample sequence to visualize
print("calling show",flush=True)
show(unet, Xval, yval, figname = 'sample.png')

#--------------------------------------------------------------------------------
# permutation evaluation of importance
# evaluate importance of each field by scrambling it and seeing how
#      much worse the predictions get
#---------------------------------------------------------------------
print("calling permute ",flush=True)
permute(unet, Xval, yval, nlayer)

