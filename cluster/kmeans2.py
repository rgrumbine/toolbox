import sys
import numpy as np
import pygrib
import netCDF4


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

"""
from reader import *

#----------------------------------------------------------
# ndarray to save for use in finding clusters
countmax = 14123456
fmax     = int(countmax/5)
#countmax = 225488
ary = np.zeros((countmax,17))
dr  = np.zeros((countmax,66+12))
ice = 14 

count = 0
for mm in (1,2,3,4,5,6):
  tag = datetime.datetime(2025,mm,2)
  print(tag, flush=True)
  count = read(tag, ary, dr, count, fmax = fmax)

count = min(count, countmax)
print(count, " points to consider", flush=True)

# Subtract off the 12th Tb (37V) since linear correlation is always very high (> 0.7, usually > 0.9)
#k = 11
#for i in range(0,11):
#    model = np.polynomial.polynomial.Polynomial.fit(ary[:count,k], ary[:count,i], 1)
#    model = model.convert().coef
#    print(model)
#    ary[:count,i] -= model[0] + model[1]*ary[:count,k]
#
#k = 7
#for i in range(0,11):
#  if (i != k):
#    model = np.polynomial.polynomial.Polynomial.fit(ary[:count,k], ary[:count,i], 1)
#    model = model.convert().coef
#    print(model)
#    ary[:count,i] -= model[0] + model[1]*ary[:count,k]
#
#print("\n post")
#for i in range(0,12):
#    for j in range(i+1,12):
#        x = np.corrcoef(ary[:count,i], ary[:count,j])
#        print("correlate ",i,j,x[0,1])
#debug: exit(0)

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

for nlim in range(6,9):
  acount = np.zeros((nlim))
  ccount = np.zeros((nlim))

  print("\nkmeans with nlim = ",nlim)
  fout = open("fout."+"{:02d}".format(nlim), "w")
  beta = KMeans(n_clusters = nlim, random_state = 0).fit(dr[:count,:])
  y_pred = beta.fit_predict(dr[:count,:])

  for k in range(0,nlim):
    for l in range(0,len(dr[0,:]) ):
      print("{:7.2f}".format(beta.cluster_centers_[k][l]),end=" ")
    print("", flush=True)

  #print("inertia ",beta.inertia_, flush=True)
  # computationally expensive -- much more than everything else combined
  #print("silhouette ",silhouette_score(ary, beta.labels_), flush=True)

  # print out cluster assignments
  for i in range(0, count):
    for k in range(0,17):
      print("{:6.2f}".format(ary[i, k]), end=" ", file=fout)
    print("c {:d}".format(y_pred[i]) , file=fout)
    # accumulate for bayes computation
    ccount [ y_pred[i] ] += 1
    if (ary[i, ice] > 0):
      acount [ y_pred[i] ] += 1

  allice   = acount.sum()
  allcount = ccount.sum()
  pice     = allice / count
  pice_given_class = np.zeros((nlim))
  pclass_given_ice = np.zeros((nlim))
  tot = 0
  for k in range(0, nlim):
    pclass = ccount[k] / count
    pice_given_class[k] = acount[k] / ccount[k]
    pclass_given_ice[k] = pice_given_class[k] * pclass / pice
    print("bayes", k,"{:.3f}".format(pice) , "{:.3f}".format(pclass) , 
            "{:.3f}".format(pice_given_class[k]) , 
            "{:.3f}".format(pclass_given_ice[k]), flush=True )
    if pice_given_class[k] > 0.9:
        tot += pclass

  fout.close()

  print("total high quality ice fraction ",tot)
