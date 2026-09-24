''' 
Single layer CNN to predict an index (NAO, NINO3.4, etc.) 
  from NSIDC monthly sea ice grids
Robert Grumbine
12 June 2026
'''
import sys
import os
from math import sqrt

import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc

import tensorflow as tf
from tensorflow.keras import models, layers
import joblib

#---------------------------------------------------------------------

def build_grid_to_scalar_cnn(grid_shape):
    model = models.Sequential([
        # 1. Feature Extraction Blocks
        layers.Input(shape=grid_shape),

        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        #layers.AvgPool2D((4, 4)),

        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        #layers.AvgPool2D((2, 2)),

        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        #layers.MaxPooling2D((2, 2)),

        #layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
        #layers.MaxPooling2D((2, 2)),

        #layers.Conv2D(512, (3, 3), activation='relu', padding='same'),

        # 2. Bridge spatial data to 1D vector
        #layers.GlobalAveragePooling2D(),
        # use flattening if location in input space matters
        layers.Flatten(),

        # 3. Regression Head
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.2), # Prevents the model from memorizing the grid noise

        # Output precisely ONE continuous scalar value
        layers.Dense(1, activation='linear')
    ])

    # Use Mean Squared Error or Mean Absolute Error for scalar regression
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
    return model


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

#---------------------------------------------------------------------
# Establish cnn model
# nh nsidc grid
#nx = 304
#ny = 448
# sh nsidc grid
nx = 316
ny = 332
#RG: spliced grid 780x316 deep, stacking one on the other?
grid_shape = (ny, nx, 1)

model = build_grid_to_scalar_cnn(grid_shape)

# --- 3. Implement Early Stopping ---
# Climate data is scarce; early stopping prevents the model from overfitting
# once the validation loss stops improving.
early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=7,
    restore_best_weights=True
)

#---------------------------------------------------------------------

# Acquire data
#   x-train = time series of ice concentration grids (ntime, grid_shape)
#   y-train = soi, nino 3.4, whatever
# then x-val, y-val
# finally x-test, y-test

ntrain = 372
nval   =  24
ntest  =  24
starting = 1989 # some kind of problem with 1988/01

y_train = np.zeros((ntrain))
y_val   = np.zeros((nval))
y_test  = np.zeros((ntest))
#-------------------
#read in month by month nsidc mean grids starting from Starting / 01 
X_train = np.zeros((ntrain, ny, nx, 1))
X_val   = np.zeros((nval, ny, nx, 1))
X_test  = np.zeros((ntest, ny, nx, 1))

count = 0
for yy in range(starting, starting+int(ntrain/12)):
  for mm in range(1,13):
    fname = shname(yy, mm)
    #debug: print(fname, flush=True)
    analy = nc.Dataset(fname)
    tmp2 = analy.variables['cdr_seaice_conc_monthly'][0,:,:]
    deflag(tmp2)
    X_train[count,:,:,0] = tmp2
    analy.close()
    count += 1

count = 0
#_val
for yy in range(starting+int(ntrain/12), starting+int(ntrain/12)+int(nval/12)):
  for mm in range(1,13):
    fname = shname(yy, mm)
    #debug: print(fname, flush=True)
    analy = nc.Dataset(fname)
    #X_val[count,:,:,0] = analy.variables['cdr_seaice_conc_monthly'][0,:,:]
    tmp2 = analy.variables['cdr_seaice_conc_monthly'][0,:,:]
    deflag(tmp2)
    X_val[count,:,:,0] = tmp2
    analy.close()
    count += 1

count = 0
#_test
for yy in range(starting+int(ntrain/12)+int(nval/12), starting+int(ntrain/12)+int(nval/12)+int(ntest/12) ):
  for mm in range(1,13):
    fname = shname(yy, mm)
    analy = nc.Dataset(fname)
    tmp2 = analy.variables['cdr_seaice_conc_monthly'][0,:,:]
    deflag(tmp2)
    X_test[count,:,:,0] = tmp2
    analy.close()
    count += 1

m = X_train.max()
X_train /= m
X_val   /= m
X_test  /= m

#-------------------
# RG would loop over idx here
# Read in all index values
full = []
#fin = open("sstoi.indices", "r", encoding='utf-8')
#idx:
#0 NINO1+2
#1 " " anom
#2 NINO3
#3 " " anom
#4 NINO4
#5 " " anom
#6 NINO3.4
#7 " " anom
#idx=7

fin = open("telecon.indices", "r", encoding='utf-8')
#idx :  0 = aao, 1 = ao, 2 = nao, 3 = pna
idx = int(sys.argv[1])

# Read in the entire span of the index file
k = 0
for line in fin:
    if (k == 0):
        k += 1
        continue
    words=line.split()
    full.append( (words[0], words[1], words[2+idx]) )
fin.close()

# ---------- Extract the target at targetted lead
# RG would loop over lead here
mlead  =   int(sys.argv[2])

for i in enumerate(full):
    #debug: print(i[0], i[1][0], flush=True)
    if int(i[1][0]) == starting:
        for j in range(i[0], i[0]+ntrain):
            y_train[j-i[0]] = float(full[j+mlead][2])

        for j in range(i[0]+ntrain, i[0]+ntrain+nval):
            y_val[j-i[0]-ntrain] = float(full[j+mlead][2])

        for j in range(i[0]+ntrain+nval, i[0]+ntrain+nval+ntest):
            y_test[j-i[0]-ntrain-nval] = float(full[j+mlead][2])

        break

#---------------------------------------------------------------------

# Train the model
print("\n\n\n\n")
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=16, # Smaller batch sizes generally perform better on small climate sets
    callbacks=[early_stopping]
)

y_pred = model.predict(X_test)

def stats(x, y):
    r = np.corrcoef(x, y)[0,1]
    z = y
    z -= x
    mean = z.sum()/len(x)
    za = np.abs(z)
    mae = za.sum()/len(x)
    z *= z
    rms = z.sum()/len(x)
    rms = sqrt(rms)
    return float(mean), float(mae), float(rms), float(r)

fout = open("out_"+f"{idx:d}"+"_"+f"{mlead:03d}"+".txt", "w", encoding="utf-8")
yp = np.zeros((ntest))
for i in range(0, ntest):
    print(i, y_test[i], y_pred[i][0], file = fout)
    yp[i] = y_pred[i][0]
#RG: compute me, mae, rms, correlation between test and pred
print(stats(y_test, yp), file = fout )
fout.close()

#---------------------------------------------------------------------
# For explainable AI -- saliency map
sample_grid   = X_test[0:1]
sample_tensor = tf.convert_to_tensor(sample_grid, dtype=tf.float32)
with tf.GradientTape() as tape:
    tape.watch(sample_tensor)
    # Forward pass through your trained model
    prediction = model(sample_tensor)

gradients = tape.gradient(prediction, sample_tensor)

# 4. Post-process the gradients
# Take the absolute value and average across the time/lag channels
saliency = np.abs(gradients.numpy()[0])
saliency = np.mean(saliency, axis=-1)

# 5. Normalize between 0 and 1 for visualization
saliency = (saliency - saliency.min()) / (saliency.max() - saliency.min() + 1e-10)

# 6. Plot the attention map overlaying your original grid
plt.figure(figsize=(10, 4))
plt.imshow(saliency, cmap='YlOrRd', origin='upper')
plt.title("Saliency Map: Where the Model is Looking: "+f"{idx:d}"+"_"+f"{mlead:03d}")
plt.colorbar(label="Importance Weight")
plt.savefig("shsalience"+f"{idx:d}"+"_"+f"{mlead:03d}"+".png")

#---------------------------------------------------------------------
# Save the model
joblib.dump(model, 'trained'+f"{mlead:03d}"+'.joblib')
#---------------------------------------------------------------------
# This is where a loop over leads would end
