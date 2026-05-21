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
    #iytrain[i] = int(5*qflags[i])
    iytrain[i] = 0
    if ytrain[i] > 0 and qflags[i] < 0.3:
        iytrain[i] = 1

xnew = xtrain[nfit:int(2*nfit), : ]
ynew = iytrain[nfit:int(2*nfit) ]

#--------------------------------------------------------------------------
from sklearn.ensemble import StackingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree      import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm      import SVC

#--------------------------------------------------------------------------
stacking_clf = StackingClassifier(
  estimators = [
      ('lr', LogisticRegression(random_state=42, max_iter = 600 )),
      ('rf', RandomForestClassifier(random_state=42)),
      ('gbc', GradientBoostingClassifier(random_state=42)),
      ('knc', KNeighborsClassifier()),
      ('dtc', DecisionTreeClassifier(max_depth=1)),
      ('svc', SVC(probability=True, random_state=42))
      ],
  final_estimator=RandomForestClassifier(random_state=43),
  cv = 5
)
class_score = np.zeros((6))

xin = [0,1,2,3,4,5,6,7]
stacking_clf.fit(xtrain[:nfit, xin ], iytrain[:nfit])

# scores for individual classifier, then stacker
i = 0
for name, clf in stacking_clf.named_estimators_.items():
    class_score[i] = clf.score(xnew[:, xin ], ynew)
    i += 1
    print('name = ',name,' score ', clf.score(xnew[:, xin ], ynew) )
stack_score = stacking_clf.score(xnew[:, xin ], ynew)
print("stacker ",stacking_clf.score(xnew[:, xin ], ynew) )
if (stack_score < class_score.max() ):
    print('stacker is actually a detriment, at ',stack_score)
    idx = np.argmax(class_score)
    print('best is individual ',idx, 'with score of ',class_score[idx])

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

if (stack_score >= class_score.max() ):
  joblib.dump(stacking_clf, 'stacking_clf.joblib')
else:
  print("joblib.dump(stacking_clf[idx]", base_model_names[idx])
  print(stacking_clf.estimators_[idx] )
  joblib.dump(stacking_clf.estimators_[idx], 'best_individual.joblib')
  for i in range(0, len(base_model_names)):
    joblib.dump(stacking_clf.estimators_[i], base_model_names[i]+'.joblib')
