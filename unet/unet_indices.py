import os
from math import sin, cos, pi
import datetime

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, Input
import matplotlib.pyplot as plt

import netCDF4 as nc


starting = 1989
nmonths  = 360
ndata = 12*(2025-1989)
# ---------------------------------------------------------
# 1. acquire data from monthly NSIDC sea ice grids
def nhname(fyy, fmm):
  ym = 100*fyy+fmm
  for inst in 'n07', 'F08', 'F11', 'F13', 'F17', 'am2':
    ftmp = 'nhmon/sic_psn25_'+f"{ym:6d}"+'_'+inst+'_v06r00.nc'
    if os.path.exists(ftmp):
      return ftmp
  return ""

def shname(fyy, fmm):
  ym = 100*fyy+fmm
  for inst in 'n07', 'F08', 'F11', 'F13', 'F17', 'am2':
    ftmp = 'shmon/sic_pss25_'+f"{ym:6d}"+'_'+inst+'_v06r00.nc'
    if os.path.exists(ftmp):
      return ftmp
  return ""

def deflag(tmp):
    tmp[tmp > 100] = 0

# Read in full index file
fin = open("telecon.indices", "r", encoding='utf-8')
full = []
# Read in the entire span of the index file
k = 0
for line in fin:
    if (k == 0):
        k += 1
        continue
    words=line.split()
    full.append( (words[0], words[1], words[2], words[3], words[4], words[5]) )
fin.close()

indices = np.zeros((ndata, 4))
for i in enumerate(full):
    if int(i[1][0]) == starting:
        istart = int(i[0])
        #debug: print("istart = ",istart, flush=True)
        #debug: print("full(istart) = ",full[istart])
        for j in range(0, ndata):
            indices[j,0] = float(full[j+istart][2] )
            indices[j,1] = float(full[j+istart][3] )
            indices[j,2] = float(full[j+istart][4] )
            indices[j,3] = float(full[j+istart][5] )

# ---------------------------------------------------------
# Input (X): Sea ice concentration at time (t-1, t-2), cos(month), sin(month), cos(2*x), sin(2x)
#    -- AAO, AO, NAO, PNA indices
# Target (y): Sea ice concentration at time (t)

nx = 304
ny = 448
nlayer = 11
nlag = 2
X_data = np.zeros((ndata, ny, nx, nlayer))
y_data = np.zeros((ndata, ny, nx, 1))

first = datetime.datetime(starting,1,1)
dt = datetime.timedelta(1)
count = 0
for yy in range(starting, starting+int(ndata/12)):
  for mm in range(1,13):
    now = datetime.datetime(yy, mm, 1)
    ttt = ((now - first)/dt)/3652.5
    fname = nhname(yy, mm)
    #debug: print(fname, flush=True)
    analy = nc.Dataset(fname)
    tmp2 = analy.variables['cdr_seaice_conc_monthly'][0,:,:]
    analy.close()
    deflag(tmp2)
    X_data[count,:,:,0] = tmp2
    X_data[count,:,:,1] = cos(2.*pi*mm/12.)
    X_data[count,:,:,2] = sin(2.*pi*mm/12.)
    X_data[count,:,:,3] = cos(2*2.*pi*mm/12.)
    X_data[count,:,:,4] = sin(2*2.*pi*mm/12.)

    X_data[count,:,:,6] = indices[count,0]
    X_data[count,:,:,7] = indices[count,1]
    X_data[count,:,:,8] = indices[count,2]
    X_data[count,:,:,9] = indices[count,3]

    X_data[count,:,:,10] = ttt

    count += 1
# Scale ice concentrations, sin, cos, time, and indices are already scaled
m = X_data[:,:,:,0].max()
X_data[:,:,:,0] /= m
for i in range(0, count-nlag):
    X_data[i,:,:,5] = X_data[i+1,:,:,0]

# now assign next month (of X_data) to y_data
for i in range(0, count-nlag):
    y_data[i,:,:,0] = X_data[i+nlag,:,:,0]
yy=starting + int(ndata/12) + 1
mm=1
fname = nhname(yy,mm)
analy = nc.Dataset(fname)
tmp2 = analy.variables['cdr_seaice_conc_monthly'][0,:,:]
analy.close()
deflag(tmp2)
y_data[count-1,:,:,0] = tmp2/m


# Train/Validation Split
split = nmonths

X_train, X_val = X_data[:split], X_data[split:-nlag]
y_train, y_val = y_data[:split], y_data[split:-nlag]

del X_data, y_data

print("ndata split ",ndata, split)

# ---------------------------------------------------------
# 2. Build the U-Net Architecture
# ---------------------------------------------------------
def double_conv_block(x, n_filters):
    # Two consecutive Convolutional layers with ReLU activation and Batch Normalization
    x = layers.Conv2D(n_filters, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(n_filters, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    return x

def build_unet(input_shape=(64, 64, 1)):
    inputs = Input(shape=input_shape)

    # --- ENCODER (Contracting Path) ---
    # Block 1: 64x64 -> Down to 32x32
    c1 = double_conv_block(inputs, 32)
    p1 = layers.MaxPooling2D((2, 2))(c1)

    # Block 2: 32x32 -> Down to 16x16
    c2 = double_conv_block(p1, 64)
    p2 = layers.MaxPooling2D((2, 2))(c2)

    # Block 3: 16x16 -> Down to 8x8
    c3 = double_conv_block(p2, 128)
    p3 = layers.MaxPooling2D((2, 2))(c3)

    # RG Block 4: 
    d4 = double_conv_block(p3, 256)
    p4 = layers.MaxPooling2D((2, 2))(d4)

    # --- BOTTLENECK ---
    # Lowest point of the U-Net (8x8 feature map)
    #bottleneck = double_conv_block(p3, 256)
    bottleneck = double_conv_block(p4, 512)

    # RG Decoder block
    u3 =  layers.Conv2DTranspose(256, (2, 2), strides=(2, 2), padding="same")(bottleneck)
    concat3 = layers.concatenate([u3, d4]) # Skip connection from Encoder Block 4
    d5 = double_conv_block(concat3, 256)

    # --- DECODER (Expanding Path with Skip Connections) ---
    # Block 4: Up to 16x16
    #u4 = layers.Conv2DTranspose(128, (2, 2), strides=(2, 2), padding="same")(bottleneck)
    u4 = layers.Conv2DTranspose(128, (2, 2), strides=(2, 2), padding="same")(d5)
    concat4 = layers.concatenate([u4, c3]) # Skip connection from Encoder Block 3
    c4 = double_conv_block(concat4, 128)


    # Block 5: Up to 32x32
    u5 = layers.Conv2DTranspose(64, (2, 2), strides=(2, 2), padding="same")(c4)
    concat5 = layers.concatenate([u5, c2]) # Skip connection from Encoder Block 2
    c5 = double_conv_block(concat5, 64)

    # Block 6: Up to 64x64
    u6 = layers.Conv2DTranspose(32, (2, 2), strides=(2, 2), padding="same")(c5)
    concat6 = layers.concatenate([u6, c1]) # Skip connection from Encoder Block 1
    c6 = double_conv_block(concat6, 32)

    # --- OUTPUT LAYER ---
    # 1x1 convolution maps the features back to 1 channel (Predicted Ice Concentration)
    # Sigmoid clamps output values strictly between 0 and 1
    outputs = layers.Conv2D(1, (1, 1), padding="same", activation="sigmoid")(c6)

    model = models.Model(inputs, outputs, name="Sea_Ice_UNet")
    return model

# ---------------------------------------------------------
# Instantiate and compile the model
unet_model = build_unet(input_shape=(ny, nx, nlayer))
unet_model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
# Print out the model description:
unet_model.summary()

print('done creating and compiling the unet model')
#debug: exit(0)

# ---------------------------------------------------------
# 3. Train the Model
# ---------------------------------------------------------
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=7, restore_best_weights=True)

history = unet_model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=30,
    batch_size=16,
    callbacks=[early_stopping]
)

# Save the model:
import joblib
joblib.dump(unet_model, "index_model.joblib")

# ---------------------------------------------------------
# 4. Predict and Visualize
# ---------------------------------------------------------
predictions = unet_model.predict(X_val)

# Extract a sample sequence to visualize
sample_idx = 0
fig, ax = plt.subplots(1, 3, figsize=(15, 5))

# Input Grid (t-1)
im0 = ax[0].imshow(X_val[sample_idx,:,:,0].squeeze(), cmap='Blues_r', origin='upper', vmin=0, vmax=1)
ax[0].set_title("Input Sea Ice Grid (t-1)")
fig.colorbar(im0, ax=ax[0])

# True Output Grid (t)
im1 = ax[1].imshow(y_val[sample_idx].squeeze(), cmap='Blues_r', origin='upper', vmin=0, vmax=1)
ax[1].set_title("True Sea Ice Grid (t)")
fig.colorbar(im1, ax=ax[1])

# U-Net Prediction (t)
im2 = ax[2].imshow(predictions[sample_idx].squeeze(), cmap='Blues_r', origin='upper', vmin=0, vmax=1)
ax[2].set_title("U-Net Predicted Grid (t)")
fig.colorbar(im2, ax=ax[2])

plt.tight_layout()
#plt.show()
plt.savefig('index_sample.png')
