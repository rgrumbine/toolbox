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

# open posteriori file
#   read in to llgrid, 1/12th
post = netCDF4.Dataset("posteriori.nc")
lat = post.variables['lat'][:,:]
lon = post.variables['lon'][:,:]
flag = post.variables['posteriori'][:,:]

#debug: print(lat.max(), lat.min(), lon.max(), lon.min(), flag.max(), flag.min(), file=sys.stderr )

# open sst file for day
#   read in (grib manage lat-lon?)
# open A file for day
#   read in (grib manage lat-lon?)

#scan tb file for day
#  if lr in line:
#    write back out with posteriori flag, sst, A

fin = open("amsr2_20250102.txt.1","r")
sst = pygrib.open("nsst/20250102/rtgssthr_grb_0.083.grib2")
conc = pygrib.open("analy/seaice_analysis.20250102/seaice.t00z.5min.grb.grib2")
sstlats,sstlons = sst[1].latlons()
icelats, icelons = conc[1].latlons()

svals = sst[1].values
avals = conc[1].values


# ndarray to save for use in finding clusters
countmax = 2254885
#countmax = 225488
ary = np.zeros((countmax,23))
pr  = np.zeros((countmax,6))
ice = 20 

count = 0
for line in fin:
  if ('lr' in line):
    words = line.split()
    tlat = float(words[1])
    tlon = float(words[2])
    # find ti, tj for posteriori (and sst, conc) grid
    tj = int(np.rint(0.5+(tlat - 90 + 1./24.)/(-1./12.)))
    ti = int(np.rint(0.5+(tlon -      1./24.)/(1./12.)))

    #if (svals[tj, ti] > 278.15):
    if (flag[tj, ti] <= 164):
      continue

    for k in range(0,12):
      ary[count,k] = float(words[k+3])

    for l in range(0,6):
      ary[count,12+l] = (ary[count,2*l] - ary[count,2*l+1])/(ary[count,2*l] + ary[count,2*l+1])
      pr[count,l] = (ary[count,2*l] - ary[count,2*l+1])/(ary[count,2*l] + ary[count,2*l+1])

    ary[count,18] = flag[tj, ti]
    ary[count,19] = svals[tj, ti]
    ary[count,20] = avals[tj, ti]
    ary[count,21] = tlat
    ary[count,22] = tlon

    count += 1

  if (count >= countmax):
    break

count = min(count, countmax)
print(count, " points to consider")
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

print("\n post")
for i in range(0,12):
    for j in range(i+1,12):
        x = np.corrcoef(ary[:count,i], ary[:count,j])
        print("correlate ",i,j,x[0,1])
#debug: exit(0)

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

for nlim in range(128,129):
  acount = np.zeros((nlim))
  ccount = np.zeros((nlim))

  print("\nkmeans with nlim = ",nlim)
  fout = open("fout."+"{:02d}".format(nlim), "w")
  beta = KMeans(n_clusters = nlim, random_state = 0).fit(ary[:count,0:18])
  y_pred = beta.fit_predict(ary[:count,0:18])

  prclust = KMeans(n_clusters = nlim, random_state = 0).fit(pr[:count,:])
  ypr_pred = prclust.fit_predict(pr[:count,:])

  for k in range(0,nlim):
    for l in range(0,18):
      print("{:7.2f}".format(beta.cluster_centers_[k][l]),end=" ")
    print("", flush=True)

  for k in range(0, nlim):
    for l in range(0,6):
      print("{:7.2f}".format(prclust.cluster_centers_[k][l]),end=" ")
    print("",flush=True)

  hist,bins = np.histogram(ypr_pred,bins=nlim)
  print(hist)
  print(bins)
  print("inertia ",prclust.inertia_, flush=True)
  # computationally expensive -- much more than everything else combined
  #print("silhouette ",silhouette_score(ary, beta.labels_), flush=True)

  # print out cluster assignments
  for i in range(0, count):
    for k in range(0,23):
      print("{:6.2f}".format(ary[i, k]), end=" ", file=fout)
    print("c {:d}".format(y_pred[i]) , file=fout)
    # accumulate for bayes computation
    #ccount [ y_pred[i] ] += 1
    #if (ary[i, ice] > 0):
    #  acount [ y_pred[i] ] += 1
    ccount [ ypr_pred[i] ] += 1
    if (ary[i, ice] > 0):
      acount [ ypr_pred[i] ] += 1

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
    print(k,"{:.3f}".format(pice) , "{:.3f}".format(pclass) , "{:.3f}".format(pice_given_class[k]) , "{:.3f}".format(pclass_given_ice[k]), flush=True )
    if pice_given_class[k] > 0.9:
        tot += pclass

  fout.close()

  print("total high quality ice fraction ",tot)
