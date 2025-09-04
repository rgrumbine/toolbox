import sys
import numpy as np
import copy

#---------------------------------------------------------------
#  Functions
def gapfill1(tsi):
  count = 0
  for i in range(1,len(tsi)-1):
    if (tsi[i] == 0 and tsi[i-1] > 0 and tsi[i+1] > 0):
      tsi[i] = 0.5*(tsi[i-1] + tsi[i+1])
      count += 1
  return count

def rescale(tsi):
   tsi -= 1.5
   tsi /= 10
def unscale(tsi):
   tsi *= 10
   tsi += 1.5

def extract(length, lead, tsi, pred, target):
  npred = 0
  for i in range(0,count-length-lead):
      pred[npred,:] = tsi[i:i+length]
      if (pred[npred].min() > 0):
        target[npred] = tsi[i+length+lead]
        if target[npred] > 0:
            #debug: print(pred[npred], target[npred])
            npred += 1
  rescale(pred)
  rescale(target)
  print("found ",npred,"predictor-target pairs")
  return npred

#---------------------------------------------------------------
# Begin main program
fin = open(sys.argv[1],"r")
nmax = int(1461*8)
tsi = np.zeros((nmax))

count = 0
for line in fin:
    words = line.split(',')
    tsi[count] = float(words[3])
    count += 1
    if (count == nmax):
        break
print(tsi.max(), tsi.min(), count )
z = tsi[1:]-tsi[:-1]
print(z.max(), z.min() )
for i in range(0,len(z)):
  if (abs(z[i]) > 0.5 ):
    print(i,"daily delta",z[i],tsi[i])
#debug: exit(0)

length = 8
ratio = 2
lead  = 1

pred   = np.zeros((nmax, length))
target = np.zeros((nmax))
npred  = extract(length, lead, tsi, pred, target)

x_train_full = pred[:npred]
x_test       = pred[:npred]
y_train_full = target[:npred]
y_test       = target[:npred]
x_train, y_train = x_train_full[:-365], y_train_full[:-365]
x_valid, y_valid = x_train_full[-365:], y_train_full[-365:]
ypersist = copy.deepcopy(y_train_full[-365-lead:-lead])
print("persist max min sum",ypersist.max(), ypersist.min(), ypersist.sum(), len(ypersist) )
print(x_train.shape, x_train.dtype)
#debug: exit(0)

import tensorflow as tf

tf.random.set_seed(1)
model = tf.keras.Sequential()
model.add(tf.keras.layers.Input(shape=[length,]))
model.add(tf.keras.layers.Flatten() )
model.add(tf.keras.layers.Dense(length*ratio, activation="relu"))
model.add(tf.keras.layers.Dense(length*ratio, activation="relu"))
model.add(tf.keras.layers.Dense(length*ratio, activation="relu"))
model.add(tf.keras.layers.Dense(1, activation="relu"))

print(model.summary() )

optimizer = tf.keras.optimizers.Adam(learning_rate=1.e-3)
model.compile(loss = 'mse',
              optimizer=optimizer,
#              metrics=['mse'])
              metrics=['RootMeanSquaredError'])

history = model.fit(x_train, y_train, epochs=30, validation_data=(x_valid, y_valid) )

mse, rmse = model.evaluate(x_test, y_test)
print("mse, rmse = ",mse, rmse)

ypred = model.predict(x_valid)
print(ypred.max(), ypred.min(), ypred[33], len(ypred) )
print(y_valid.max(), y_valid.min(), y_valid[33], len(y_valid) )

#-------------------------------------------------------------
# Return to original scaling
unscale(ypred)
unscale(y_valid)
unscale(ypersist)


print("persist max min sum",ypersist.max(), ypersist.min(), ypersist.sum(), len(ypersist) )
print("ypred max min sum",ypred.max(), ypred.min(), ypred.sum(), len(ypred) )
print("valid max min sum",y_valid.max(), y_valid.min(), y_valid.sum(), len(y_valid) )

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg') #for batch mode

fig,ax = plt.subplots()
ax.set(xlabel = "N")

t = np.linspace(0,len(y_valid),len(y_valid))

ax.plot(t,y_valid, color='black', label='obs')
ax.plot(t,ypred, color='blue', label = 'nn')
ax.plot(t,ypersist, color='red', label = 'persist')
ax.legend()
ax.grid()
plt.savefig("test.png")

#------------------ computing bias, rmse by hand
predsum      = 0.
predsumsq    = 0.
persistsum   = 0.
persistsumsq = 0.
for i in range(0,len(y_valid)):
  ypred[i]     -= y_valid[i]
  predsum      += ypred[i]
  predsumsq    += ypred[i]**2
  ypersist[i]  -= y_valid[i]
  persistsum   += ypersist[i]
  persistsumsq += ypersist[i]**2

from math import *
print("persist max min sum",ypersist.max(), ypersist.min(), ypersist.sum() )
print("persist mean, rms ",persistsum/365, sqrt(persistsumsq/365))

print("predict max min sum",ypred.max(), ypred.min(), ypred.sum() )
print("predict mean, rms ",ypred.sum()/365, predsum/365, sqrt(predsumsq/365))

print("rmse persist pred",sqrt(persistsumsq/365), sqrt(predsumsq/365) )
#----------------------------------------------
fig,ax = plt.subplots()
ax.set(xlabel = "N")

ax.plot(t,ypred, color='blue', label = 'nn')
ax.plot(t,ypersist, color='red', label = 'persist')
ax.legend()
ax.grid()
plt.savefig("delta.png")
#----------------------------------------------

model.save("arctic_model.keras")
