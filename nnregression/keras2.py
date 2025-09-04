import sys
import numpy as np

import tensorflow as tf

#---------------------------------------------------------------
#  Functions
def gapfill1(tsi):
  count = 0
  for i in range(1,len(tsi)-1):
    if (tsi[i] == 0 and tsi[i-1] > 0 and tsi[i+1] > 0):
      tsi[i] = 0.5*(tsi[i-1] + tsi[i+1])
      count += 1
  return count

def extract(length, lead, tsi, pred, target):
  npred = 0
  for i in range(0,count-length-lead):
      pred[npred,:] = tsi[i:i+length]
      if (pred[npred].min() > 0):
        target[npred] = tsi[i+length+lead]
        if target[npred] > 0:
            #debug: print(pred[npred], target[npred])
            npred += 1
  pred   -= 1360.
  target -= 1360.
  print("found ",npred,"predictor-target pairs")
  return npred

#---------------------------------------------------------------
# Begin main program
fin = open(sys.argv[1],"r")
nmax = 2782
tsi = np.zeros((nmax))

count = 0
for line in fin:
    words = line.split()
    tsi[count] = float(words[4])
    count += 1
#print(tsi.max(), tsi.min() )
print("gaps filled: ",gapfill1(tsi))

length = 5
lead  = 1
ratio = 3
pred   = np.zeros((nmax, length))
target = np.zeros((nmax))

npred  = extract(length, lead, tsi, pred, target)

x_train_full = pred[:npred]
x_test       = pred[:npred]
y_train_full = target[:npred]
y_test       = target[:npred]
x_train, y_train = x_train_full[:-200], y_train_full[:-200]
x_valid, y_valid = x_train_full[-200:], y_train_full[-200:]
print(x_train.shape, x_train.dtype)

tf.random.set_seed(42)
model = tf.keras.Sequential()
model.add(tf.keras.layers.Input(shape=[length,]))
model.add(tf.keras.layers.Flatten() )
model.add(tf.keras.layers.Dense(length*ratio, activation="relu"))
model.add(tf.keras.layers.Dense(length*ratio, activation="relu"))
model.add(tf.keras.layers.Dense(length*ratio, activation="relu"))
model.add(tf.keras.layers.Dense(1, activation="relu"))
print("hello7", flush=True)

print(model.summary() )

optimizer = tf.keras.optimizers.Adam(learning_rate=1.e-3)
print("hello8", flush=True)
model.compile(loss = 'mse',
              optimizer=optimizer,
              metrics=['mse'])
print("hello9", flush=True)

history = model.fit(x_train, y_train, epochs=30, validation_data=(x_valid, y_valid) )

mse, rmse = model.evaluate(x_test, y_test)
print("mse, rmse = ",mse, rmse)

