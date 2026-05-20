import sys
import joblib
import copy

import numpy as np
import netCDF4 as nc

# note this should be an ssmis file -- f285 or f286
data = nc.Dataset(sys.argv[1], "r")
nobs = len(data.dimensions['nobs'])

xtrain = np.zeros((nobs, 8))
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

#land[:]     = data.variables['land_flag'][:]
#land   /= 0.99
#xtrain[:,8] = land
#
#qflags[:]   = data.variables['quality'][:]
#qflags /= 5.
#xtrain[:,9] = qflags


iytrain = ytrain.astype(np.int_)
nfit = min(30*1000, int(nobs/2-1) )
#for i in range(0,2*nfit):
for i in range(0,nobs):
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
      ('dtc', DecisionTreeClassifier()),
      ('svc', SVC(probability=True, random_state=42))
      ],
  final_estimator=RandomForestClassifier(random_state=43),
  cv = 5
)
class_score = np.zeros((6))

xin = [0,1,2,3,4,5,6,7]
stacking_clf.fit(xtrain[:nfit, xin ], iytrain[:nfit])
ystack = stacking_clf.predict(xnew[:, xin ])

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
#----------------------------------------------------------------------------

#----------------------------------------------------------------------------
# Above constructs a classifier. Now make a regressor using only 
#   what the classifier says is non-zero
#    values
count = 0
# this is still categorical
ypredall = stacking_clf.estimators_[idx].predict(xtrain[:,xin])

xtrain2 = []
ytrain2 = []
for i in range(0, nobs):
  if ypredall[i] == 1:
  #if ypredall[i] == 0:
      xtrain2.append(xtrain[i,:])
      ytrain2.append(ytrain[i])
      count += 1
print("found ",count,"points to regress on", flush=True)
xnew2 = np.zeros((count,8))
ynew2 = np.zeros((count))
for i in range(0, count):
    #xnew2[i,:] = xtrain2[i,xin]
    ynew2[i]   = ytrain2[i]
    xnew2[i,:] = xtrain2[i]

from sklearn.ensemble import StackingRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree     import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso

# ---- Calling the functions manually -- does not remove need to call stacker.fit
from math import sqrt
def contingency(obs, pred):
    n1 = len(obs)
    n2 = len(pred)
    if (n1 != n2):
        print("rgrms unequal vector sizes, exiting",n1, n2)
        sys.exit(0)
    a00 = 0
    a10 = 0
    a01 = 0
    a11 = 0
    for i in range(0,n1):
        if obs[i] == 0:
            if pred[i] == 0:
                a00 += 1
            else:
                a01 += 1
        elif pred[i] == 0:
            a10 += 1
        else:
            a11 += 1
    return (a00,a01,a10,a11)

def rgrms(obs, pred):
    n1 = len(obs)
    n2 = len(pred)
    if (n1 != n2):
        print("rgrms unequal vector sizes, exiting",n1, n2)
        sys.exit(0)
    sumx = 0.
    sumx2 = 0.
    for i in range(0, n1):
      sumx += pred[i]-obs[i]
      sumx2 += (pred[i]-obs[i])*(pred[i]-obs[i])
    sumx /= n1
    sumx2 /= n1
    return sqrt(sumx2)

rf = RandomForestRegressor(random_state=42)
rf.fit(xnew2[:nfit,:], ynew2[:nfit] )
rf_predict = rf.predict(xnew2[nfit:int(2*nfit), :] )
joblib.dump(rf, 'random_forest.joblib')
for i, score in enumerate(rf.feature_importances_):
    print(f"RF {i}: {score:.4f}", flush=True)
print("rf score ",rgrms(rf_predict, ynew2[nfit:int(2*nfit)]), 
        rf.score(xnew2[nfit:int(2*nfit), :], ynew2[nfit:int(2*nfit)]) , flush=True)

lr = LinearRegression()
lr.fit(xnew2[:nfit,:], ynew2[:nfit] )
lrpred = lr.predict(xnew2[nfit:int(2*nfit), :] )
joblib.dump(lr, 'linear_regression.joblib')
print("lr score ",rgrms(lrpred, ynew2[nfit:int(2*nfit)]),
        lr.score(xnew2[nfit:int(2*nfit), :], ynew2[nfit:int(2*nfit)]) , flush=True)

lasso = Lasso(random_state=42)
lasso.fit(xnew2[:nfit,:], ynew2[:nfit] )
lassopred = lasso.predict(xnew2[nfit:int(2*nfit), :] )
joblib.dump(lasso, 'lasso.joblib')
print("lasso score ",rgrms(lassopred, ynew2[nfit:int(2*nfit)]),
        lasso.score(xnew2[nfit:int(2*nfit), :], ynew2[nfit:int(2*nfit)]) , flush=True)

dt = DecisionTreeRegressor()
dt.fit(xnew2[:nfit,:], ynew2[:nfit] )
dtpred = dt.predict(xnew2[nfit:int(2*nfit), :])
joblib.dump(dt, 'decision_tree.joblib')
print("dt score ",rgrms(dtpred, ynew2[nfit:int(2*nfit)]),
        dt.score(xnew2[nfit:int(2*nfit), :], ynew2[nfit:int(2*nfit)]) , flush=True)

print('zzzzz',flush=True)
ytmp = copy.deepcopy(ynew2[nfit:int(2*nfit)])
avg = ytmp.sum() / len(ytmp)
for i in range(0,len(ytmp)):
    ytmp[i] = avg

print(len(ytmp), rgrms(ytmp, ynew2[nfit:int(2*nfit)]))
#----------------------------------------------------

rf_predict = rf.predict(xnew2[nfit:, :] )
#for i in range(nfit, count):
#    print(i,ynew2[i], rf_predict[i-nfit])

print(rgrms(rf_predict, ynew2[nfit:]) )

print(contingency(iytrain, ypredall))
