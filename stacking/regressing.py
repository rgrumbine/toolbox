import sys

import numpy as np
import netCDF4 as nc

from sklearn.ensemble import StackingRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree     import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso

#-------------------------------------------------------------
# note this should be an ssmis file -- f285 or f286
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
#xtrain /= 300.

ytrain[:] = data.variables['ice_concentration'][:]
ytrain *= 100

nfit = min(30*1000, int(nobs/2-1) )
xnew = xtrain[nfit:int(2*nfit), : ]
ynew = ytrain[nfit:int(2*nfit) ]

#--------------------------------------------------------------------------
import joblib

# ---- Calling the functions manually -- does not remove need to call stacker.fit
rf = RandomForestRegressor(random_state=42)
rf.fit(xtrain[:nfit,:], ytrain[:nfit] )
rf_predict = rf.predict(xnew)
joblib.dump(rf, 'random_forest.joblib')

lr = LinearRegression()
lr.fit(xtrain[:nfit,:], ytrain[:nfit] )
lrpred = lr.predict(xnew)
joblib.dump(lr, 'linear_regression.joblib')

lasso = Lasso(random_state=42)
lasso.fit(xtrain[:nfit,:], ytrain[:nfit] )
lassopred = lasso.predict(xnew)
joblib.dump(lasso, 'lasso.joblib')

dt = DecisionTreeRegressor()
dt.fit(xtrain[:nfit,:], ytrain[:nfit] )
dtpred = dt.predict(xnew)
joblib.dump(dt, 'decision_tree.joblib')

print('zzzzz',flush=True)
print(rf.score(xnew,ynew), lr.score(xnew, ynew), lasso.score(xnew,ynew), dt.score(xnew,ynew)  )

#--------------------------------------------------------------------------
# Using pre-trained estimators
stacker = StackingRegressor(
  estimators = [
      ('rf', rf),
      ('lr', lr),
      ('lasso', lasso),
      ('dectree', dt)
      ],
  final_estimator=RandomForestRegressor(random_state=43),
  cv = 5
)

stacker.fit(xtrain[:nfit,:], ytrain[:nfit])
ystack = stacker.predict(xnew)
for i in range(0,nfit):
    print(i, ystack[i], ynew[i])

# scores for individual classifier, then stacker
for name, clf in stacker.named_estimators_.items():
    print('name = ',name,' score ', clf.score(xnew, ynew) )
print("stacker ",stacker.score(xnew, ynew) )

# feature importance -------------------------------------------------
# Extract names from your estimators list
base_model_names = [name for name, clf in stacker.estimators]

# Map them to the final estimator's importances
importances = stacker.final_estimator_.feature_importances_

for name, score in zip(base_model_names, importances):
    print(f"Base Model: {name:5} | Importance to Stacker: {score:.4f}")

# From the base model's random forest
base_rf = stacker.named_estimators_['rf']
for i, score in enumerate(base_rf.feature_importances_):
    print(f"RF {i}: {score:.4f}")

# From the base model's decision tree 
base = stacker.named_estimators_['dectree']
for i, score in enumerate(base.feature_importances_):
    print(f"DT {i}: {score:.4f}")
