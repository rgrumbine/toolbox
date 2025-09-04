import sys
import numpy as np
from math import *

from sklearn.metrics         import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.neural_network  import MLPRegressor
from sklearn.pipeline        import make_pipeline
from sklearn.preprocessing   import StandardScaler
from sklearn.linear_model import LinearRegression

#---------------------------------------------------------------
fin = open(sys.argv[1],"r")
nmax = 2782
tsi = np.zeros((nmax))

count = 0
for line in fin:
    words = line.split()
    tsi[count] = float(words[4])
    count += 1
#print(tsi.max(), tsi.min() )

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
  pred   -= 1360.
  target -= 1360.
  print("found ",npred,"predictor-target pairs")
  return npred

#----------------------------------------------------------
lead   = 16
target = np.zeros((nmax))

length = 5
for length in range (2,35):
  pred   = np.zeros((nmax, length))
  npred  = extract(length, lead, tsi, pred, target)
  
  x_train_full, x_test, y_train_full, y_test = train_test_split(pred[:npred], target[:npred], random_state=42)
  x_train, x_valid, y_train, y_valid = train_test_split(x_train_full, y_train_full, random_state=42)
  
  for ratio in range (1,8):
    #3: mlp_reg = MLPRegressor(hidden_layer_sizes=[ratio*length,ratio*length,ratio*length], random_state=42)
    #2: mlp_reg = MLPRegressor(hidden_layer_sizes=[ratio*length,ratio*length], random_state=42)
    #1: 
    mlp_reg = MLPRegressor(hidden_layer_sizes=[ratio*length], random_state=42)
    pipeline = make_pipeline(StandardScaler(), mlp_reg)
    pipeline.fit(x_train, y_train)
    y_pred = pipeline.predict(x_valid)
    rmse = mean_squared_error(y_valid, y_pred)
    print("length ",length,"depth 1 ratio",ratio,"rmse: ",rmse)
  

#----------------------------------------------------------
  model = LinearRegression()
  model.fit(x_train, y_train)
  yp = model.predict(x_valid)
  
  sumsq = 0
  for i in range(0,len(x_valid)):
      sumsq += (yp[i]-y_valid[i])**2
  print("length ",length,"linear regression rmse", sqrt(sumsq/len(x_valid)) )

#----------------------------------------------------------
# try predicting N days out by iterating the 1 day prediction N times
#----------------------------------------------------------

t = np.linspace(0,len(x_valid),len(x_valid))

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
