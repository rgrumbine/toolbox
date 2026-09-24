''' only use observations more 'distant' than some limit from each other '''

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
def dist(x1, x2, mindist):
    tmp = x1-x2
    tmp *= tmp
    #debug: print('dist ',tmp.sum() )
    return tmp.sum() > mindist

xdist = []
ydist = []
mindist = 1./256.

xdist.append(xtrain[0,:])
ydist.append(ytrain[0])
count = 1
start = time.time()
for i in range(1,int(nobs/1) ):
  ok = True
  for j in range(0,count):
      ok = ok and dist(xdist[j], xtrain[i], mindist)
      if not ok:
          break
  if ok:
      xdist.append(xtrain[i])
      ydist.append(ytrain[i])
      #debug: print("added ",i, flush=True)
      count += 1

print("count = ",count, len(xdist))
print('time to ensure distinct ',time.time() - start)
if (count < 30):
    for i in range(0, count):
        print(xdist[i])
    
