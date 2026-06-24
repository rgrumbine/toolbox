''' relag --
  Build a unet to predict sea ice concentration grids given:
    previous 2 months
    time, cos(time), sin(time), cos(2*time), sin(2*time),
    AAO, AO, NAO, PNA indices
  Then do permutation on each to estimate importance

  Clean up lag references

  Robert Grumbine
  23 June 2026 '''

import sys
import os
from math import sin, cos, pi
import datetime

import numpy as np
import netCDF4 as nc

import tensorflow as tf
from tensorflow.keras import layers, models, Input
import matplotlib.pyplot as plt
import joblib

starting = 1989
nmonths  = 360 # training span
ndata = 12*(2025-1989)
nlag  = 2
# ---------------------------------------------------------
# 1. acquire data from monthly NSIDC sea ice grids
def nhname(fyy, fmm):
  ''' nhname(fyy, fmm) -- return nsidc nh monthly file name for year and month '''
  ym = 100*fyy+fmm
  for inst in 'n07', 'F08', 'F11', 'F13', 'F17', 'am2':
    ftmp = 'nhmon/sic_psn25_'+f"{ym:6d}"+'_'+inst+'_v06r00.nc'
    if os.path.exists(ftmp):
      return ftmp
  return ""

def shname(fyy, fmm):
  ''' shname(fyy, fmm) -- return nsidc sh monthly file name for year and month '''
  ym = 100*fyy+fmm
  for inst in 'n07', 'F08', 'F11', 'F13', 'F17', 'am2':
    ftmp = 'shmon/sic_pss25_'+f"{ym:6d}"+'_'+inst+'_v06r00.nc'
    if os.path.exists(ftmp):
      return ftmp
  return ""

def deflag(tmp):
    ''' deflag(tmp) -- remove NSIDC flags from grid '''
    tmp[tmp > 100] = 0


# ---------------------------------------------------------
# Input (X): Sea ice concentration at time (t-1, t-2), cos(month), sin(month), cos(2*x), sin(2x)
# Target (y): Sea ice concentration at time (t)

nx = 304
ny = 448
nlayer = 6
X_data = np.zeros((ndata, ny, nx, nlayer))

first = datetime.datetime(starting,1,1)
dt = datetime.timedelta(1)

# Predict from (lag 1 date)
yy = 2024
mm = 12

fname = nhname(yy, mm)
analy = nc.Dataset(fname)
tmp2 = analy.variables['cdr_seaice_conc_monthly'][0,:,:]
analy.close()
deflag(tmp2)
X_data[0,:,:,1] = tmp2 # lag 1

mmold = mm - 1
if (mmold == 0):
    yy -= 1
    mmold = 12
fname = nhname(yy, mmold)
analy = nc.Dataset(fname)
tmp2 = analy.variables['cdr_seaice_conc_monthly'][0,:,:]
analy.close()
deflag(tmp2)
X_data[0,:,:,0] = tmp2 # lag 2
X_data[0,:,:,2] = cos(2.*pi*(mm+nlag-1)/12.)
X_data[0,:,:,3] = sin(2.*pi*(mm+nlag-1)/12.)
X_data[0,:,:,4] = cos(2*2.*pi*(mm+nlag-1)/12.)
X_data[0,:,:,5] = sin(2*2.*pi*(mm+nlag-1)/12.)


# ---------------------------------------------------------
# load the model
if os.path.exists("index_model.joblib"):
  model = joblib.load("index_model.joblib")
else:
  print("could not find model to make predictions with")
  sys.exit(0)

# Print out the model description:
model.summary()

# ---------------------------------------------------------
# 4. Predict and Visualize
# ---------------------------------------------------------
print('\n\n\n\n')

starter = np.zeros((1, ny, nx, nlayer))
starter = X_data
print('starter shape',starter.shape)
print("yy, mm ",yy,mm)


for i in range(0, 12):
  mm += 1
  if (mm == 13):
      mm = 1
      yy += 1
  starter[0,:,:,2] = cos(2.*pi*(mm+nlag-1)/12.)
  starter[0,:,:,3] = sin(2.*pi*(mm+nlag-1)/12.)
  starter[0,:,:,4] = cos(2*2.*pi*(mm+nlag-1)/12.)
  starter[0,:,:,5] = sin(2*2.*pi*(mm+nlag-1)/12.)

  predictions = model.predict(starter)
  #debug: print('predictions shape',predictions.shape, flush=True)

  # Plot the input and predicted month
  sample_idx = 0
  fig, ax = plt.subplots(1, 3, figsize=(15, 5))
  
  # Input Grid (t-1)
  im0 = ax[0].imshow(starter[sample_idx,:,:,1].squeeze(), cmap='Blues_r',
          origin='upper', vmin=0, vmax=1)
  ax[0].set_title("Input Sea Ice Grid (t-1)")
  fig.colorbar(im0, ax=ax[0])
  
  # U-Net Prediction (t)
  im1 = ax[1].imshow(predictions[sample_idx].squeeze(), cmap='Blues_r',
          origin='upper', vmin=0, vmax=1)
  ax[1].set_title(f"U-Net Predicted Grid (t) {yy:4d},{mm:02d}")
  fig.colorbar(im1, ax=ax[1])

  # Verification:
  fname = nhname(yy, mm)
  analy = nc.Dataset(fname)
  tmp2 = analy.variables['cdr_seaice_conc_monthly'][0,:,:]
  analy.close()
  deflag(tmp2)
  X_data[0,:,:,0] = tmp2
  im2 = ax[2].imshow(X_data[0,:,:,0].squeeze(), cmap='Blues_r',
          origin='upper', vmin=0, vmax=1)
  ax[2].set_title("verification")
  fig.colorbar(im2, ax=ax[2])

  plt.tight_layout()
  plt.savefig(f'prediction{yy:4d}{mm:02d}.png')

  # RG: update trig terms, swap sic-1 in to sic-2, prediction in to sic-1
  starter[0,:,:,0] = starter[0,:,:,1]
  starter[0,:,:,1] = predictions[0,:,:,0]
