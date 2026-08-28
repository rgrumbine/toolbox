import sys
import os
from math import pi, cos, sin

''' cnn3 adds saliency mapping '''

import tensorflow as tf
from tensorflow.keras import models, layers

def build_grid_to_scalar_cnn(grid_shape):
    model = models.Sequential([
        # 1. Feature Extraction Blocks
        #      e.g., (100, 100, 1) if 100x100 grid with 1 variable
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

#--------------------------------------------------------
# nh nsidc grid
grid_shape = (448, 304, 3)
# sh nsidc grid
#grid_shape = (332, 316, 1)
#RG: spliced grid 780x316 deep, stacking one on the other?

enso_model = build_grid_to_scalar_cnn(grid_shape)

# --- 3. Implement Early Stopping ---
# Climate data is scarce; early stopping prevents the model from overfitting
# once the validation loss stops improving.
early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=7,
    restore_best_weights=True
)
#----------------------------------------------------------
# Acquire data
#   x-train = time series of ice concentration grids (ntime, grid_shape)
#   y-train = soi, nino 3.4, whatever
# then x-val, y-val
# finally x-test, y-test
import netCDF4 as nc
import numpy as np

mlead  =  -0
ntrain = 384
nval   =  24
ntest  =  24
starting = 1989
y_train = np.zeros((ntrain))
y_val   = np.zeros((nval))
y_test  = np.zeros((ntest))

# Read in all index values
full = []
#fin = open("sstoi.indices")
fin = open("telecon.indices")
#idx :  0 = aao, 1 = ao, 2 = nao, 3 = pna
idx = 2

k = 0
for line in fin:
    if (k == 0):
        k += 1
        continue
    words=line.split()
    full.append( (words[0], words[1], words[2+idx]) )

#for i in range(0,len(full)):
for i in enumerate(full):
    #print(i[0], i[1][0])
    if int(i[1][0]) == starting:
        for j in range(i[0], i[0]+ntrain):
            y_train[j-i[0]] = float(full[j+mlead][2])

        for j in range(i[0]+ntrain, i[0]+ntrain+nval):
            y_val[j-i[0]-ntrain] = float(full[j+mlead][2])

        for j in range(i[0]+ntrain+nval, i[0]+ntrain+nval+ntest):
            y_test[j-i[0]-ntrain-nval] = float(full[j+mlead][2])

        break
      
#read in month by month nsidc mean grids starting from Starting - 1
X_train = np.zeros((ntrain, 448, 304, 3))
X_val   = np.zeros((nval, 448, 304, 3))
X_test  = np.zeros((ntest, 448, 304, 3))
def nsidc_name(yy, mm):
  ym = 100*yy+mm
  for inst in 'n07', 'F08', 'F11', 'F13', 'F17', 'am2':
    ftmp = 'nhmon/sic_psn25_'+f"{ym:6d}"+'_'+inst+'_v06r00.nc'
    if os.path.exists(ftmp):
      return ftmp

count = 0
for yy in range(starting, starting+int(ntrain/12)):
  for mm in range(1,13):
    fname = nsidc_name(yy, mm)
    #debug: print(fname)
    analy = nc.Dataset(fname)
    X_train[count,:,:,0] = analy.variables['cdr_seaice_conc_monthly'][0,:,:]
    X_train[count,:,:,1] = cos(2.*pi*(mm-1)/12.)
    X_train[count,:,:,2] = sin(2.*pi*(mm-1)/12.)
    analy.close()
    count += 1

count = 0
#_val
for yy in range(starting+int(ntrain/12), starting+int(ntrain/12)+int(nval/12)):
  for mm in range(1,13):
    fname = nsidc_name(yy, mm)
    #debug: print(fname, flush=True)
    analy = nc.Dataset(fname)
    X_val[count,:,:,0] = analy.variables['cdr_seaice_conc_monthly'][0,:,:]
    X_val[count,:,:,1] = cos(2.*pi*(mm-1)/12.)
    X_val[count,:,:,2] = sin(2.*pi*(mm-1)/12.)
    analy.close()
    count += 1

count = 0
#_test
for yy in range(starting+int(ntrain/12)+int(nval/12), starting+int(ntrain/12)+int(nval/12)+int(ntest/12) ):
  for mm in range(1,13):
    fname = nsidc_name(yy, mm)
    #debug: print(fname, flush=True)
    analy = nc.Dataset(fname)
    X_test[count,:,:,0] = analy.variables['cdr_seaice_conc_monthly'][0,:,:]
    analy.close()
    count += 1

#debug: print("xtrain max",X_train.max(), flush=True )
m = X_train.max()
X_train /= m
X_val   /= m
X_test  /= m


#debug: sys.exit(0)
#----------------------------------------------------------


print("\n\n\n\n")
history = enso_model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=16, # Smaller batch sizes generally perform better on small climate sets
    callbacks=[early_stopping]
)

y_pred = enso_model.predict(X_test)
#print(y_pred)
#print(y_test)
print(y_train.sum() / ntrain)

for i in range(0, ntest):
    print(i, y_test[i], y_pred[i][0])

#----------------------------------------------------------
import matplotlib.pyplot as plt

# For explainable AI -- saliency map -----------------------
sample_grid   = X_test[0:1]
sample_tensor = tf.convert_to_tensor(sample_grid, dtype=tf.float32)
with tf.GradientTape() as tape:
    tape.watch(sample_tensor)
    # Forward pass through your trained model
    prediction = enso_model(sample_tensor)

gradients = tape.gradient(prediction, sample_tensor).numpy()[0]

# 4. Post-process the gradients
# Take the absolute value and average across the time/lag channels
saliency_multilayer = np.abs(gradients)


# 5. Prep visualization
num_channels = saliency_multilayer.shape[-1]
fig, axes = plt.subplots(1, num_channels, figsize=(5 * num_channels, 4), sharey=True)
channel_labels = ["SIC", "cos", "sin"]

# 6. Plot the attention map overlaying your original grid
for i in range(0, num_channels):
  channel_sal = saliency_multilayer[:,:,i]
  channel_sal = (channel_sal - channel_sal.min() )/(channel_sal.max() - channel_sal.min() + 1.e-10)
  
  im = axes[i].imshow(channel_sal, cmap = 'hot', origin='upper')
  axes[i].set_title(channel_labels[i])

fig.colorbar(im, ax=axes.ravel().tolist(), label="Relative Importance", shrink=0.6)
plt.show()
#plt.savefig("salience.png")
