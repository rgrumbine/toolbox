import sys
import joblib

import numpy as np
import netCDF4 as nc

# note this should be an ssmis file -- f285 or f286
data = nc.Dataset(sys.argv[1], "r")
nobs = len(data.dimensions['nobs'])

xtrain = np.zeros((nobs, 10))
ytrain = np.zeros((nobs))
qflags = np.zeros((nobs))
land   = np.zeros((nobs))

ytrain[:] = data.variables['ice_concentration'][:]

xtrain[:,0] = data.variables['tb_19V'][:]
xtrain[:,1] = data.variables['tb_19H'][:]
xtrain[:,2] = data.variables['tb_22V'][:]
xtrain[:,3] = data.variables['tb_37V'][:]
xtrain[:,4] = data.variables['tb_37H'][:]
xtrain[:,5] = data.variables['tb_92V'][:]
xtrain[:,6] = data.variables['tb_92H'][:]
xtrain[:,7] = data.variables['tb_150H'][:]
# scaling towards a 0-1 range:
xtrain /= 300.
land[:]     = data.variables['land_flag'][:]
land   /= 0.99
xtrain[:,8] = land

qflags[:]   = data.variables['quality'][:]
qflags /= 5.
xtrain[:,9] = qflags


iytrain = ytrain.astype(np.int_)
nfit = min(10*1000, int(nobs/2-1) )
for i in range(0,2*nfit):
    iytrain[i] = 0
    if ytrain[i] > 0:
        iytrain[i] = 1

xnew = xtrain[nfit:int(2*nfit), : ]
ynew = iytrain[nfit:int(2*nfit) ]

#--------------------------------------------------------------------------
from sklearn.ensemble import StackingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm      import SVC

#--------------------------------------------------------------------------
stacking_clf = StackingClassifier(
  estimators = [
      ('lr', LogisticRegression(random_state=42, max_iter = 600 )),
      ('rf', RandomForestClassifier(random_state=42)),
      ('svc', SVC(probability=True, random_state=42))
      ],
  final_estimator=RandomForestClassifier(random_state=43),
  cv = 5
)

stacking_clf.fit(xtrain[:nfit,:], iytrain[:nfit])
ystack = stacking_clf.predict(xnew)
for i in range(0,nfit):
  if (ystack[i] != ynew[i]):
    print(i, ystack[i], ynew[i], qflags[i+nfit], land[i+nfit])

# scores for individual classifier, then stacker
for name, clf in stacking_clf.named_estimators_.items():
    print('name = ',name,' score ', clf.score(xnew, ynew) )
print("stacker ",stacking_clf.score(xnew, ynew) )

# feature importance -------------------------------------------------
# Extract names from your estimators list
base_model_names = [name for name, clf in stacking_clf.estimators]

# Map them to the final estimator's importances
importances = stacking_clf.final_estimator_.feature_importances_

for name, score in zip(base_model_names, importances):
    print(f"Base Model: {name:5} | Importance to Stacker: {score:.4f}")

# For the base model's random forest
base_rf = stacking_clf.named_estimators_['rf']
for i, score in enumerate(base_rf.feature_importances_):
    print(f"Original Feature {i}: {score:.4f}")

joblib.dump(stacking_clf, 'stacking_clf.joblib')
