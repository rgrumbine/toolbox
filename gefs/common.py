''' unet for GEFS sea ice prediction from many atmospheric fields '''

import numpy as np
import matplotlib.pyplot as plt

#import tensorflow as tf
from tensorflow.keras import layers, models, Input

#--------------------------------------------------------------

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

def build_unet(input_shape=(768, 1536, 1), final='relu', nchannel = 1):
    inputs = Input(shape=input_shape)

    # Encoding:
    # Block 1 768x1536 -> 768x768
    c1 = double_conv_block(inputs, 32)
    p1 = layers.MaxPooling2D((1,2))(c1)

    # Block 2: 768 -> 384
    c2 = double_conv_block(p1, 64)
    p2 = layers.MaxPooling2D((2,2))(c2)

    # Block 3: 384 -> 192
    c3 = double_conv_block(p2, 128)
    p3 = layers.MaxPooling2D((2,2))(c3)

    # Block 4: 192 -> 96
    c4 = double_conv_block(p3, 256)
    p4 = layers.MaxPooling2D((2,2))(c4)

    # Block 5: 96 -> 48
    c5 = double_conv_block(p4, 512)
    p5 = layers.MaxPooling2D((2,2))(c5)

    # Block 6: 48 -> 24
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

    u6 = layers.Conv2DTranspose(32, (1,2), strides = (1,2), padding="same")(c11)
    concat6 = layers.concatenate([u6,c1])
    c12 = double_conv_block(concat6, 32)

    
    # Output layer:
    outputs = layers.Conv2D(nchannel, (1,1), padding="same", activation=final)(c12)

    model = models.Model(inputs, outputs, name="GEFS")
    return model

#--------------------------------------------------------------------------------
# permutation evaluation of importance
# evaluate importance of each field by scrambling it and seeing how
#      much worse the predictions get
#---------------------------------------------------------------------
def permute(unet, Xval, yval, nlayer):
    #debug: print('entered permute',nlayer,flush=True)
  baseline_mse = unet.evaluate(Xval, yval, verbose=0)[0]
  #debug: print('past initial evaluation',flush=True)

  importance = np.zeros((nlayer))
  for i in range(0, nlayer):
      #debug: print("evaluating layer ",i,flush=True)
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
      print(f"{i:02d}", 'importance', f"{importance[i]:11.4e}", f"{importance[i]/baseline_mse:11.4e}")


#--------------------------------------------------------------------------------
def show(unet, Xval, yval, figname = 'summary.png'):
  #debug: print("entered show",figname,flush=True)
  #debug: unet.summary()
  #debug: print(flush=True)

  # Extract a sample sequence to visualize
  predictions = unet.predict(Xval)
  #debug: print("show made prediction", flush=True)

  sample_idx = 0
  fig, ax = plt.subplots(1, 3, figsize=(15, 5))

  # Input Grid (t-1)
  # RG: note 0-1 favors a 'Blues' color bar. 'seismic' for +-1
  im0 = ax[0].imshow(Xval[sample_idx,:,:,0].squeeze(), cmap='seismic', origin='lower', vmin=-1, vmax=1)
  ax[0].set_title("Input Grid (t-1)")
  fig.colorbar(im0, ax=ax[0])

  # True Output Grid (t)
  im1 = ax[1].imshow(yval[sample_idx].squeeze(), cmap='seismic', origin='lower', vmin=-1, vmax=1)
  ax[1].set_title("True Grid (t)")
  fig.colorbar(im1, ax=ax[1])

  # U-Net Prediction (t)
  im2 = ax[2].imshow(predictions[sample_idx].squeeze(), cmap='seismic', origin='lower', vmin=-1, vmax=1)
  ax[2].set_title("U-Net Predicted Grid (t)")
  fig.colorbar(im2, ax=ax[2])

  plt.tight_layout()
  plt.savefig(figname)
  plt.close()
