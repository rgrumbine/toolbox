import sys
import joblib
import time

import numpy as np
import netCDF4 as nc

start = time.time() 
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

iytrain = ytrain.astype(np.int_)
nfit = min(512*1000, int(nobs/2-1) )
for i in range(0,2*nfit):
    #iytrain[i] = int(5*qflags[i])
    iytrain[i] = 0
    if ytrain[i] > 0 and qflags[i] < 0.3:
        iytrain[i] = 1

xnew = xtrain[nfit:int(2*nfit), : ]
ynew = iytrain[nfit:int(2*nfit) ]

print("time to read in and set up data",time.time() - start)

#--------------------------------------------------------------------------
from sklearn.ensemble import StackingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree      import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm      import SVC

#--------------------------------------------------------------------------
lr = LogisticRegression(random_state=42, max_iter = 600 )
start = time.time()
lr.fit(xtrain[:nfit,:], iytrain[:nfit])
lrtime = time.time() - start
print("lr",lrtime)

rf = RandomForestClassifier(random_state=42)
start = time.time()
rf.fit(xtrain[:nfit,:], iytrain[:nfit])
rftime = time.time() - start
print("rf",rftime)

gbc = GradientBoostingClassifier(random_state=42)
start = time.time()
gbc.fit(xtrain[:nfit,:], iytrain[:nfit])
gbctime = time.time() - start
print("gbc",gbctime)

knc = KNeighborsClassifier()
start = time.time()
knc.fit(xtrain[:nfit,:], iytrain[:nfit])
knctime = time.time() - start
print("knc",knctime)

dtc = DecisionTreeClassifier()
start = time.time()
dtc.fit(xtrain[:nfit,:], iytrain[:nfit])
dtctime = time.time() - start
print("dtc",dtctime)

#svc = SVC(probability=True, random_state=42)
#start = time.time()
#svc.fit(xtrain[:nfit,:], iytrain[:nfit])
#svctime = time.time() - start
#print("svc",svctime)

#-----------------------------------------------------------------
#stacking_clf = StackingClassifier(
#  estimators = [
#      ('lr', lr),
#      ('rf', rf),
#      ('gbc', gbc),
#      ('knc', knc),
#      ('dtc', dtc)
##      ('svc', svc)
#      ],
#  #final_estimator=RandomForestClassifier(random_state=43),
#  final_estimator=DecisionTreeClassifier(),
#  cv = 5
#)
#class_score = np.zeros((6))
#
#start = time.time()
#stacking_clf.fit(xtrain[:nfit, : ], iytrain[:nfit])
#print('stacker time ',time.time() - start)
#
## scores for individual classifier, then stacker
#i = 0
#for name, clf in stacking_clf.named_estimators_.items():
#    class_score[i] = clf.score(xnew[:, : ], ynew)
#    i += 1
#    print('name = ',name,' score ', clf.score(xnew[:, : ], ynew) )
#stack_score = stacking_clf.score(xnew[:, : ], ynew)
#print("stacker ",stacking_clf.score(xnew[:, : ], ynew) )
#
#
#if (stack_score < class_score.max() ):
#    print('stacker is actually a detriment, at ',stack_score)
#    idx = np.argmax(class_score)
#    print('best is individual ',idx, 'with score of ',class_score[idx])
#
#-----------------------------------------------------------------
stack2 = StackingClassifier(
  estimators = [
      ('lr', lr),
      ('rf', rf),
      ('gbc', gbc),
      ('knc', knc),
      ('dtc', dtc)
      ],
  final_estimator=RandomForestClassifier(random_state=43),
  #final_estimator=DecisionTreeClassifier(),
  cv = 5
)

start = time.time()
stack2.fit(xtrain[:nfit, : ], iytrain[:nfit])
print('stack2 time ',time.time() - start)

# scores for individual classifier, then stacker
i = 0
class_score = np.zeros((6))
for name, clf in stack2.named_estimators_.items():
    class_score[i] = clf.score(xnew[:, : ], ynew)
    i += 1
    print('name = ',name,' score ', clf.score(xnew[:, : ], ynew) )
stack_score = stack2.score(xnew[:, : ], ynew)
print("stack2 ",stack2.score(xnew[:, : ], ynew) )


if (stack_score < class_score.max() ):
    print('stacker2 is actually a detriment, at ',stack_score)
    idx = np.argmax(class_score)
    print('best is individual ',idx, 'with score of ',class_score[idx])

#-----------------------------------------------------------------
