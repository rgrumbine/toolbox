import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, Input
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. Generate Synthetic Sequential Grid Data (For Demo)
# ---------------------------------------------------------
# Let's simulate 500 timesteps of 64x64 grids.
# Input (X): Sea ice concentration at time (t-1)
# Target (y): Sea ice concentration at time (t)
num_samples = 500
grid_size = 64

# Simulating smooth spatial fields bounded between 0.0 and 1.0 (0% to 100% ice)
X_data = np.random.uniform(0, 1, (num_samples, grid_size, grid_size, 1)).astype(np.float32)
# The target is a slightly shifted/evolved version of the input to simulate melting/freezing
y_data = np.clip(X_data * 0.9 + np.random.normal(0, 0.05, X_data.shape), 0, 1).astype(np.float32)

# Train/Validation Split
split = int(0.8 * num_samples)
X_train, X_val = X_data[:split], X_data[split:]
y_train, y_val = y_data[:split], y_data[split:]

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

    # --- BOTTLENECK ---
    # Lowest point of the U-Net (8x8 feature map)
    bottleneck = double_conv_block(p3, 256)

    # --- DECODER (Expanding Path with Skip Connections) ---
    # Block 4: Up to 16x16
    u4 = layers.Conv2DTranspose(128, (2, 2), strides=(2, 2), padding="same")(bottleneck)
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

# Instantiate and compile the model
unet_model = build_unet(input_shape=(grid_size, grid_size, 1))
unet_model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
unet_model.summary()

# ---------------------------------------------------------
# 3. Train the Model
# ---------------------------------------------------------
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

history = unet_model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=20,
    batch_size=16,
    callbacks=[early_stopping]
)

# ---------------------------------------------------------
# 4. Predict and Visualize
# ---------------------------------------------------------
predictions = unet_model.predict(X_val)

# Extract a sample sequence to visualize
sample_idx = 0
fig, ax = plt.subplots(1, 3, figsize=(15, 5))

# Input Grid (t-1)
im0 = ax[0].imshow(X_val[sample_idx].squeeze(), cmap='Blues_r', origin='lower', vmin=0, vmax=1)
ax[0].set_title("Input Sea Ice Grid (t-1)")
fig.colorbar(im0, ax=ax[0])

# True Output Grid (t)
im1 = ax[1].imshow(y_val[sample_idx].squeeze(), cmap='Blues_r', origin='lower', vmin=0, vmax=1)
ax[1].set_title("True Sea Ice Grid (t)")
fig.colorbar(im1, ax=ax[1])

# U-Net Prediction (t)
im2 = ax[2].imshow(predictions[sample_idx].squeeze(), cmap='Blues_r', origin='lower', vmin=0, vmax=1)
ax[2].set_title("U-Net Predicted Grid (t)")
fig.colorbar(im2, ax=ax[2])

plt.tight_layout()
plt.show()