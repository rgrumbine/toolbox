'''
predicting tsi from sorce observations
'''
import sys
from math import sqrt

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from sklearn.metrics         import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.neural_network  import MLPRegressor
from sklearn.pipeline        import make_pipeline
from sklearn.preprocessing   import StandardScaler
from sklearn.linear_model import LinearRegression

def gapfill1(ftsi):
  ''' gapfill1(tsi) -- fill in single step observation gaps by linear interpolation '''
  fcount = 0
  for fi in range(1,len(ftsi)-1):
    if (ftsi[fi] == 0 and ftsi[fi-1] > 0 and ftsi[fi+1] > 0):
      ftsi[fi] = 0.5*(ftsi[fi-1] + ftsi[fi+1])
      fcount += 1
  return fcount

#---------------------------------------------------------------
fin = open(sys.argv[1],"r", encoding="utf-8")
nmax = 2782
nmax = int(365*4)
tsi = np.zeros((nmax))

#ch06 header is 134 lines
for i in range(0,134):
  fin.readline()

count = 0
for line in fin:
    words = line.split()
    tsi[count] = float(words[4])
    count += 1
    if (count == nmax):
        break
print(tsi.max(), tsi.min() )

print("gaps filled: ",gapfill1(tsi))

#----------------------------------------------------------

def extract(flength, flead, ftsi, fpred, ftarget):
  ''' extract(length, lead, tsi, pred, target) '''
  fnpred = 0
  for i in range(0,count-flength-flead):
      fpred[fnpred,:] = ftsi[i:i+flength]
      if (fpred[fnpred].min() > 0):
        ftarget[fnpred] = ftsi[i+flength+flead]
        if ftarget[fnpred] > 0:
            #debug: print(fpred[fnpred], ftarget[fnpred])
            fnpred += 1
  fpred   -= 1360.
  ftarget -= 1360.
  print("found ",fnpred,"predictor-target pairs")
  return fnpred

def train(fnmax, flength, flead, fratio, ftsi, fpred, target, fbest, plot = False):
  ''' train(nmax, length, lead, fratio, tsi, pred, target, best) '''
  fpred   = np.zeros((fnmax, flength))
  npred  = extract(flength, flead, ftsi, fpred, target)

  x_train_full, x_test, y_train_full, y_test = train_test_split(fpred[:npred], 
                                                   target[:npred], random_state=42)
  x_train, x_valid, y_train, y_valid = train_test_split(x_train_full, y_train_full, 
                                                   random_state=42)

  #3: 3 layer multilayer perceptron
  mlp_reg = MLPRegressor(hidden_layer_sizes=[fratio*flength,fratio*flength,fratio*flength], random_state=42)
  #2: mlp_reg = MLPRegressor(hidden_layer_sizes=[fratio*flength,fratio*flength], random_state=42)
  #1: mlp_reg = MLPRegressor(hidden_layer_sizes=[fratio*flength], random_state=42)
  pipeline = make_pipeline(StandardScaler(), mlp_reg)
  pipeline.fit(x_train, y_train)
  y_pred = pipeline.predict(x_valid)
  rmse = mean_squared_error(y_valid, y_pred)
  if (rmse < fbest[0]):
      fbest[0] = rmse
      fbest[1] = fratio
      fbest[2] = flength
  print("length ",flength,"depth 1 ratio",fratio,"rmse: ",rmse, fbest)

  #----------------------------------------------------------
  model = LinearRegression()
  model.fit(x_train, y_train)
  yp = model.predict(x_valid)

  sumsq = 0
  for fi in range(0,len(x_valid)):
      sumsq += (yp[fi]-y_valid[fi])**2
  print("length ",length,"linear regression rmse", sqrt(sumsq/len(x_valid)), len(y_valid), flush=True )

  return npred, yp, y_pred, y_valid

#----------------------------------------------------------
lead   = 16
target = np.zeros((nmax))

best = np.zeros((3))
best[0] = 99.

for ratio in range (1,8):
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
print("results with best")
print(yp.max(), y_pred.max(), y_valid.max(), len(y_valid))
print(yp.min(), y_pred.min(), y_valid.min(), len(y_valid))

t = np.linspace(0,len(y_valid),len(y_valid))

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
