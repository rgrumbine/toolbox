import sys
import numpy as np
import pygrib
import netCDF4
import datetime

"""
run for each day

splice together:
    lr scans
    posteriori flag
    sst
    sea ice concentration (L4)

find clusters:
    12 Tb channels
    "" augmented by posteriori, sst, A
       augmented by PR

"""

from reader import *

#---------------------------------------------------------

# ndarray to save for use in finding clusters
countmax = 9123456
fmax = int(countmax/4)
#fmax = 10000
ary = np.zeros((countmax,23))
dr  = np.zeros((countmax,66+12))
ice = 14 

count = 0
for mm in (1,2,3,4,5,6):
  tag = datetime.datetime(2025,mm,2)
  print(tag, flush=True)
  count = read(tag, ary, dr, count, fmax = fmax)

count = min(count, countmax)
print(count, " points to consider", flush=True)

#---------------------------------------------------------
from sklearn.mixture import GaussianMixture

for nlim in range(5,9):
  acount = np.zeros((nlim))
  ccount = np.zeros((nlim))

  print("\ngaussian mixtures with nlim = ",nlim)
  fout   = open("fout."+"{:02d}".format(nlim), "w")
  fmodel = open("fmodel."+"{:02d}".format(nlim), "w")

  cluster = GaussianMixture(n_components = nlim, random_state = 0).fit(dr[:count,:])
  y_pred  = cluster.predict(dr[:count,:])
  # read these back in to hot start for downstream applications
  print(cluster.n_components, file = fmodel)
  print(cluster.weights_, file = fmodel)
  print(cluster.means_, file = fmodel)
  #print(cluster.covariances_, file = fmodel)

  for k in range(0,nlim):
    for l in range(0,len(cluster.means_)):
      print("{:7.2f}".format(cluster.means_[k][l]),end=" ")
    print("", flush=True)

  hist,bins = np.histogram(y_pred,bins=nlim)
  print(hist)
  print(bins)
  print("did clustering converge ",cluster.converged_,cluster.n_iter_ )

  # print out cluster assignments
  for i in range(0, count):
    for k in range(0,23):
      print("{:6.2f}".format(ary[i, k]), end=" ", file=fout)
    print("c {:d}".format(y_pred[i]) , file=fout)

    ## for full suite
    ccount [ y_pred[i] ] += 1
    if (ary[i, ice] > 0):
      acount [ y_pred[i] ] += 1

  allice   = acount.sum()
  allcount = ccount.sum()
  pice     = allice / count
  pice_given_class = np.zeros((nlim))
  pclass_given_ice = np.zeros((nlim))
  tot = 0
  print("ccount",ccount)
  print("acount",acount)
  print("pice ",pice)
  for k in range(0, nlim):
    pclass = ccount[k] / count
    pice_given_class[k] = acount[k] / ccount[k]
    pclass_given_ice[k] = pice_given_class[k] * pclass / pice
    print('bayes',k,"{:.3f}".format(pice) , "{:.3f}".format(pclass) , "{:.3f}".format(pice_given_class[k]) , "{:.3f}".format(pclass_given_ice[k]), flush=True )
    if ( pice_given_class[k] > 0.89):
        tot += pclass
  #slow: print("aic, bic",cluster.aic(dr[:count,:]), cluster.bic(dr[:count,:]))
  fout.close()

  print(nlim,"total high quality ice fraction ",tot)
