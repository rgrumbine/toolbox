import sys
import joblib

import numpy as np
import netCDF4 as nc

# note this should be an ssmis file -- f285 or f286
data = nc.Dataset(sys.argv[1], "r")
nobs = len(data.dimensions['nobs'])

xtrain = np.zeros((nobs, 8))
ytrain = np.zeros((nobs))
ynew   = np.zeros((nobs))

ytrain[:] = data.variables['ice_concentration'][:]

xtrain[:,0] = data.variables['tb_19V'][:]
xtrain[:,1] = data.variables['tb_19H'][:]
xtrain[:,2] = data.variables['tb_22V'][:]
xtrain[:,3] = data.variables['tb_37V'][:]
xtrain[:,4] = data.variables['tb_37H'][:]
xtrain[:,5] = data.variables['tb_92V'][:]
xtrain[:,6] = data.variables['tb_92H'][:]
xtrain[:,7] = data.variables['tb_150H'][:]
xtrain /= 300.

iytrain = ytrain.astype(np.int_)
for i in range(0,nobs):
    iytrain[i] = 0
    if ytrain[i] > 0:
        iytrain[i] = 1
#--------------------------------------------------------------------------
from sklearn.ensemble  import StackingClassifier
from sklearn.ensemble  import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm       import SVC
from sklearn.ensemble  import GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree      import DecisionTreeClassifier
from sklearn.tree      import export_text

#--------------------------------------------------------------------------
clf = joblib.load('dtc.joblib')
#clf = joblib.load('best_individual.joblib')
#clf = joblib.load('stacking_clf.joblib')
print('clf = ',clf)
rules = export_text(clf)
print(rules)
#exit(0)

ynew = clf.predict(xtrain)
count = 0
for i in range(0, nobs):
  if (ynew[i] == iytrain[i]):
      count += 1
print("final ",count, count/nobs)
