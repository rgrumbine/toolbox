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
#--------------------------------------------------------------

# Acquire basic data -- grids for weeks/months 1-540
start = datetime.datetime(1980,1,1)
dt    = datetime.timedelta(1)
end   = datetime.datetime(1981,4,6)

nx = 1536
ny =  768
nlayer = 15
ntarget = 1
nlag    = 1
nweeks   = int((end-start)/dt/7 + 1)
print('nweeks = ',nweeks, flush=True)

tracemalloc.start()

Xdata = np.zeros((nweeks, ny, nx, nlayer), dtype=np.float32)
Xavg  = np.zeros((ny, nx, nlayer), dtype=np.float32)
# Get memory metrics: (current, peak)
current, peak = tracemalloc.get_traced_memory()
print(f"Memory usage after np.zeros: {current / 10**6} Mb")
print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)

# Get, rather than compute, an average field
getavg.getavg(Xavg, 'average_1980.nc')

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

nvar = 1 # 0 = icetk, 1 = icec, 2 = sst
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
# design the Unet -- 6 layers deep, giving 24x12 as the bottleneck grid (15 degree blocks)
# RG: 1x3 layer for fact that fields tend to vary in longitude more than latitude?
# A: No, just a 1x2 as that gives a square array which gemini says is more 
#    computationally efficient
def double_conv_block(x, n_filters):
    # Two consecutive Convolutional layers with ReLU activation and Batch Normalization
    x = layers.Conv2D(n_filters, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(n_filters, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    return x

def build_unet(input_shape=(768, 1536, 1)):
    inputs = Input(shape=input_shape)

    # Encoding:
    # Block 1 x1536 -> x384
    c1 = double_conv_block(inputs, 32)
    p1 = layers.MaxPooling2D((2,4))(c1)

    # Block 2: 768 -> 192
    c2 = double_conv_block(p1, 64)
    p2 = layers.MaxPooling2D((2,2))(c2)

    # Block 3: 384 -> 96
    c3 = double_conv_block(p2, 128)
    p3 = layers.MaxPooling2D((2,2))(c3)

    # Block 4: 192 -> 48
    c4 = double_conv_block(p3, 256)
    p4 = layers.MaxPooling2D((2,2))(c4)

    # Block 5: 96 -> 24
    c5 = double_conv_block(p4, 512)
    p5 = layers.MaxPooling2D((2,2))(c5)

    # Block 6: 48 -> 12
    c6 = double_conv_block(p5, 1024)
    p6 = layers.MaxPooling2D((2,2))(c6)


    # Bottleneck layer
    bottleneck = double_conv_block(p6, 2048)


    # Decoding block
    u1 = layers.Conv2DTranspose(1024, (2,2), strides = (2,2), padding="same")(bottleneck)
    concat1 = layers.concatenate([u1, c6])
    c7 = double_conv_block(concat1, 1024)

    u2 = layers.Conv2DTranspose(512, (2,2), strides = (2,2), padding="same")(c7)
    concat2 = layers.concatenate([u2, c5])
    c8 = double_conv_block(concat2, 512)

    u3 = layers.Conv2DTranspose(256, (2,2), strides = (2,2), padding="same")(c8)
    concat3 = layers.concatenate([u3, c4])
    c9 = double_conv_block(concat3, 256)

    u4 = layers.Conv2DTranspose(128, (2,2), strides = (2,2), padding="same")(c9)
    concat4 = layers.concatenate([u4, c3])
    c10 = double_conv_block(concat4, 128)

    u5 = layers.Conv2DTranspose(64, (2,2), strides = (2,2), padding="same")(c10)
    concat5 = layers.concatenate([u5,c2])
    c11 = double_conv_block(concat5, 64)

    u6 = layers.Conv2DTranspose(32, (2,4), strides = (2,4), padding="same")(c11)
    concat6 = layers.concatenate([u6,c1])
    c12 = double_conv_block(concat6, 32)

    
    # Output layer:
    outputs = layers.Conv2D(1, (1,1), padding="same", activation="relu")(c12)

    model = models.Model(inputs, outputs, name="GEFS_Sea_ice")
    return model


#--------------------------------------------------------------------------------
# compile, show, and train the unet -- read in an old one if available
if (os.path.exists('fast.joblib')):
  begin = time.time()
  print("about to load joblib",flush=True)
  unet = joblib.load('fast.joblib')
  print("back from load joblib",flush=True)
  print("time = ",time.time() - begin)
else:
  print("building the unet model", flush=True)
  unet = build_unet(input_shape=(ny,nx,nlayer))
  unet.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])

unet.summary() # print the model description

# Get memory metrics: (current, peak)
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 10**6} Mb")
print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)

#debug: exit(0)

early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)

history = unet.fit(
    Xtrain, ytrain,
    validation_data=(Xval, yval),
    epochs=10,
    batch_size=16,
    callbacks=[early_stopping]
)
# Get memory metrics: (current, peak)
current, peak = tracemalloc.get_traced_memory()
print(f"past training memory usage: {current / 10**6} Mb")
print(f"Peak memory usage: {peak / 10**6} Mb", flush=True)

# save the unet
joblib.dump(unet, "fast.joblib")

#debug: sys.exit(0)

#--------------------------------------------------------------------------------
# Extract a sample sequence to visualize
predictions = unet.predict(Xval)

sample_idx = 0
fig, ax = plt.subplots(1, 3, figsize=(15, 5))

# Input Grid (t-1)
im0 = ax[0].imshow(Xval[sample_idx,:,:,0].squeeze(), cmap='Blues_r', origin='lower', vmin=0, vmax=1)
ax[0].set_title("Input Sea Ice Grid (t-1)")
fig.colorbar(im0, ax=ax[0])

# True Output Grid (t)
im1 = ax[1].imshow(yval[sample_idx].squeeze(), cmap='Blues_r', origin='lower', vmin=0, vmax=1)
ax[1].set_title("True Sea Ice Grid (t)")
fig.colorbar(im1, ax=ax[1])

# U-Net Prediction (t)
im2 = ax[2].imshow(predictions[sample_idx].squeeze(), cmap='Blues_r', origin='lower', vmin=0, vmax=1)
ax[2].set_title("U-Net Predicted Grid (t)")
fig.colorbar(im2, ax=ax[2])

plt.tight_layout()
plt.savefig('sample2.png')

#--------------------------------------------------------------------------------
# permutation evaluation of importance
# evaluate importance of each field by scrambling it and seeing how
#      much worse the predictions get
#---------------------------------------------------------------------
baseline_mse = unet.evaluate(Xval, yval, verbose=0)[0]

importance = np.zeros((nlayer))
for i in range(0, nlayer):
    # Clone the validation data so we don't permanently ruin it
    X_corrupted = np.copy(Xval)

    # Shuffle the samples for just this specific channel axis
    # This keeps the grid shape intact but scrambles the data randomly
    shuffled_indices = np.random.permutation(len(Xval))
    X_corrupted[:, :, :, i] = Xval[shuffled_indices, :, :, i]

    # Evaluate the model with the scrambled channel
    corrupted_mse = unet.evaluate(X_corrupted, yval, verbose=0)[0]

    # Importance is how much worse the error got
    importance[i] = corrupted_mse - baseline_mse

for i in range(0, nlayer):
    print(i, 'importance', importance[i])
