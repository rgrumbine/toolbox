import sys
import numpy as np
from math import *

from sklearn.metrics         import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.neural_network  import MLPRegressor
from sklearn.pipeline        import make_pipeline
from sklearn.preprocessing   import StandardScaler
from sklearn.linear_model import LinearRegression

def gapfill1(tsi):
  count = 0
  for i in range(1,len(tsi)-1):
    if (tsi[i] == 0 and tsi[i-1] > 0 and tsi[i+1] > 0):
      tsi[i] = 0.5*(tsi[i-1] + tsi[i+1])
      count += 1
  return count

#---------------------------------------------------------------
fin = open(sys.argv[1],"r")
nmax = 1461*8
tsi = np.zeros((nmax))

count = 0
for line in fin:
    words = line.split(',')
    tsi[count] = float(words[3])
    count += 1
    if (count == nmax):
        break
#print(tsi.max(), tsi.min() )
print("gaps filled: ",gapfill1(tsi))

#----------------------------------------------------------

def extract(length, lead, tsi, pred, target):
  npred = 0
  for i in range(0,count-length-lead):
      pred[npred,:] = tsi[i:i+length]
      if (pred[npred].min() > 0):
        target[npred] = tsi[i+length+lead]
        if target[npred] > 0:
            #debug: print(pred[npred], target[npred])
            npred += 1
  #pred   -= 1360.
  #target -= 1360.
  print("found ",npred,"predictor-target pairs")
  return npred

def train(nmax, length, lead, ratio, tsi, pred, target, best, plot = False):
  pred   = np.zeros((nmax, length))
  npred  = extract(length, lead, tsi, pred, target)
 
  x_train_full, x_test, y_train_full, y_test = train_test_split(pred[:npred], target[:npred], random_state=42)
  x_train, x_valid, y_train, y_valid = train_test_split(x_train_full, y_train_full, random_state=42)
  
  #3: 
  mlp_reg = MLPRegressor(hidden_layer_sizes=[ratio*length,ratio*length,ratio*length], random_state=42)
  #2: mlp_reg = MLPRegressor(hidden_layer_sizes=[ratio*length,ratio*length], random_state=42)
  #1: mlp_reg = MLPRegressor(hidden_layer_sizes=[ratio*length], random_state=42)
  pipeline = make_pipeline(StandardScaler(), mlp_reg)
  pipeline.fit(x_train, y_train)
  y_pred = pipeline.predict(x_valid)
  rmse = mean_squared_error(y_valid, y_pred)
  if (rmse < best[0]):
      best[0] = rmse
      best[1] = ratio
      best[2] = length
  print("length ",length,"ratio",ratio,"rmse: ",rmse, best)

  #----------------------------------------------------------
  model = LinearRegression()
  model.fit(x_train, y_train)
  yp = model.predict(x_valid)
  
  sumsq = 0
  for i in range(0,len(x_valid)):
      sumsq += (yp[i]-y_valid[i])**2
  print("length ",length,"linear regression rmse", sqrt(sumsq/len(x_valid)), len(y_valid) )

  #debug: print(len(yp), len(y_pred), len(y_valid))

  return npred, yp, y_pred, y_valid

#----------------------------------------------------------
lead   = 31
target = np.zeros((nmax))

best = np.zeros((3))
best[0] = 99.

for ratio in range (1,6):
  for length in range (2,35):
    pred   = np.zeros((nmax, length))

    train(nmax, length, lead, ratio, tsi, pred, target, best)
    print(best)
    

#----------------------------------------------------------
# try predicting N days out by iterating the 1 day prediction N times
#----------------------------------------------------------

# ---------- Plot from the best ---------------------------

print("now trying a rerun with the best")
print(best)
ratio  = int(best[1])
length = int(best[2])

npred,yp,y_pred,y_valid = train(nmax, length, lead, ratio, tsi, pred, target, best)
print(yp.max(), y_pred.max(), y_valid.max(), len(y_valid))
print(yp.min(), y_pred.min(), y_valid.min(), len(y_valid))

t = np.linspace(0,len(y_valid),len(y_valid))

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg') #for batch mode

fig,ax = plt.subplots()
ax.set(xlabel = "N")

ax.plot(t,y_valid, color='black', label='obs')
ax.plot(t,y_pred, color='blue', label='mlp')
ax.plot(t,yp, color='red', label='lin')

ax.legend()
ax.grid()
plt.savefig("rmse.png")

y_pred -= y_valid
yp     -= y_valid
fig,ax = plt.subplots()
ax.set(xlabel = "N")

ax.plot(t,y_pred, color='blue', label='mlp')
ax.plot(t,yp, color='red', label='lin')

ax.legend()
ax.grid()
plt.savefig("delta.png")
