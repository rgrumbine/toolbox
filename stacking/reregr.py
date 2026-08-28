''' Run a pre-trained random forest regressor on the full set of data '''
import sys

import joblib
import numpy as np
import netCDF4 as nc

from sklearn.ensemble import RandomForestRegressor

# -- initialize and get random forest
#rf = RandomForestRegressor(random_state=42)
rf = joblib.load('random_forest.joblib')

# -- Get the observations
data = nc.Dataset(sys.argv[1], "r")
nobs = len(data.dimensions['nobs'])

xtrain = np.zeros((nobs, 8))
ytrain = np.zeros((nobs))

xtrain[:,0] = data.variables['tb_19V'][:]
xtrain[:,1] = data.variables['tb_19H'][:]
xtrain[:,2] = data.variables['tb_22V'][:]
xtrain[:,3] = data.variables['tb_37V'][:]
xtrain[:,4] = data.variables['tb_37H'][:]
xtrain[:,5] = data.variables['tb_92V'][:]
xtrain[:,6] = data.variables['tb_92H'][:]
xtrain[:,7] = data.variables['tb_150H'][:]

ytrain[:] = data.variables['ice_concentration'][:]
ytrain *= 100

# Make a prediction suite
ypred = rf.predict(xtrain)
sumx = 0.
sumx2 = 0.
for i in range(0,nobs):
    print(i,ypred[i], ytrain[i])
    sumx += (ypred[i] - ytrain[i])
    sumx2 += (ypred[i] - ytrain[i])* (ypred[i] - ytrain[i])

sumx /= nobs
sumx2 /= nobs
print("mean, rmse ",sumx, sumx2**0.5)
