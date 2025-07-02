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
#-----------------------------------------------------------------------
def noop():
  return
#-----------------------------------------------------------------------
def bayes(tree, dr, ary, preds, count):
    leaf = tree.apply(dr[:count])
    for ileaf in range(0, int(leaf.max())+1 ): 
      count00 = 0
      count01 = 0
      count10 = 0
      count11 = 0
      for i in range (0, count):
        if (leaf[i] == ileaf): 
          if (preds[i] == 0 and ary[i,20] == 0):
              count00 += 1
          elif (preds[i] > 0 and ary[i,20] > 0):
              count11 += 1
          elif (preds[i] == 0 and ary[i,20] > 0):
              count01 += 1
          elif (preds[i] > 0 and ary[i,20] == 0):
              count10 += 1
      tot    =  count00 + count01 + count10 + count11
      if (tot == 0):
        noop()
      elif (count10+count11 == 0):
        print(ileaf, "no ice in leaf ",tot, tot/count)
      else:
        pice   = (count01 + count11)/tot
        #pclass = (count10 + count11)/tot
        pclass = tot/count
        pice_given_class = count11/(count10+count11)
        pclass_given_ice = pice_given_class * pclass / pice
        csi = count11/(count11 + count01 + count10)
        print(ileaf,"leaf", "{:.3f}".format(pice) , "{:.3f}".format(pclass) , 
              "{:.3f}".format(pice_given_class) , "{:.3f}".format(pclass_given_ice), tot, tot/count,  "{:.3f}".format(csi), flush=True )


#--------------------------------------------------------------------------
# open posteriori file
#   read in to llgrid, 1/12th
post = netCDF4.Dataset("posteriori.nc")
lat = post.variables['lat'][:,:]
lon = post.variables['lon'][:,:]
flag = post.variables['posteriori'][:,:]

# open sst file for day
#   read in (grib manage lat-lon?)
# open A file for day
#   read in (grib manage lat-lon?)

#scan tb file for day
#  if lr in line:
#    write back out with posteriori flag, sst, A

countmax = 9123456
#countmax = 225488
fmax = int(countmax / 4)
fmax = 2000000
ice = 20 
# ndarray to save for use in finding clusters
ary   = np.zeros((countmax,23))
pr    = np.zeros((countmax,6))
dr    = np.zeros((countmax,66+12))
grpr  = np.zeros((countmax,12))
count = 0

base='/export/emc-lw-rgrumbi/rmg3/obs/seaice_analysis.'
for mm in (1,2,3,4,5):
  fcount = 0
  tag = datetime.datetime(2025,mm,28)
  print(tag)
  ymd = tag.strftime("%Y%m%d") 
  fname = base+ymd+"/amsr2_"+ymd+".txt.1"
  fin = open(fname,"r")
  sst = pygrib.open("nsst/"+ymd+"/rtgssthr_grb_0.083.grib2")
  conc = pygrib.open("analy/seaice_analysis."+ymd+"/seaice.t00z.5min.grb.grib2")

  svals = sst[1].values
  avals = conc[1].values

  for line in fin:
    if ('lr' in line):
      words = line.split()
      tlat = float(words[1])
      tlon = float(words[2])
      # find ti, tj for posteriori (and sst, conc) grid
      tj = int(np.rint(0.5+(tlat - 90 + 1./24.)/(-1./12.)))
      ti = int(np.rint(0.5+(tlon -      1./24.)/(1./12.)))
  
      # skip areas that are always warm
      if (flag[tj, ti] <= 164):
        continue
  
      for k in range(0,12):
        ary[count,k] = float(words[k+3])
  
      #for l in range(0,6):
        #ary[count,12+l] = (ary[count,2*l] - ary[count,2*l+1])/(ary[count,2*l] + ary[count,2*l+1])
        #pr[count,l]     = (ary[count,2*l] - ary[count,2*l+1])/(ary[count,2*l] + ary[count,2*l+1])
        #grpr[count,l]   = (ary[count,2*l] - ary[count,9])/(ary[count,2*l] + ary[count,9])
        #grpr[count,l+6] = pr[count,l]

      pcount = 0
      for l in range(0,12):
        for m in range(l+1,12):
          dr[count,pcount] = (ary[count,l] - ary[count,m])/(ary[count,l]+ary[count,m])
          pcount += 1
      for l in range(0,12):
        dr[count,l+66] = ary[count,l]
      #dr[count,12+66] = svals[tj,ti]
  
      ary[count,18] = flag[tj, ti]
      ary[count,19] = svals[tj, ti]
      ary[count,20] = avals[tj, ti]
      ary[count,21] = tlat
      ary[count,22] = tlon
  
      fcount += 1
      count  += 1
  
    if (fcount >= fmax):
      print('reached fmax of ',fmax, flush=True)
      fin.close()
      break
    if (count >= countmax):
      print('reached countmax of ',countmax, flush=True)
      break

  print(fcount,"read from file")
  fin.close()

count = min(count, countmax)
print(count, " points to consider v countmax",countmax, flush=True)
#---------------------------------------------------------
# make categorical (int) for decision tree
x = ary[:count,20]*100
y = x.astype(dtype=np.int32)
for i in range(0,count):
  if (y[i] > 0):
    y[i] = 1

import sklearn
from sklearn.tree import DecisionTreeClassifier

for depth in range(1,7):
  tree_clf = DecisionTreeClassifier(max_depth = depth)
  #tree_clf.fit(ary[:count,:18], y)
  #preds = tree_clf.predict(ary[:count,:18])
  tree_clf.fit(dr[:count], y)
  preds = tree_clf.predict(dr[:count])
  t     = sklearn.tree.export_text(tree_clf, max_depth = 3)
  print("\ndepth, leaves",tree_clf.get_depth(), tree_clf.get_n_leaves() )
  print("decision tree top for depth ",depth,"\n",t)

  # check leaf behavior:
  bayes(tree_clf, dr, ary, preds, count)
  
  count00 = 0
  count01 = 0
  count10 = 0
  count11 = 0
  for i in range (0, count):
    if (preds[i] == 0 and ary[i,20] == 0):
        count00 += 1
    elif (preds[i] > 0 and ary[i,20] > 0):
        count11 += 1
    elif (preds[i] == 0 and ary[i,20] > 0):
        count01 += 1
    elif (preds[i] > 0 and ary[i,20] == 0):
        count10 += 1

  #print(depth, 'c00 c01 c10 c11 ',count00, count01, count10, count11, count)
  print("depth",depth, "tot%correct ",(count00+count11)/(count00 + count01 + count10 + count11))

  pice = (count01 + count11)/count
  pclass = (count10 + count11)/count
  pice_given_class = count11/(count10+count11)
  pclass_given_ice = pice_given_class * pclass / pice
  csi = count11/(count11 + count01 + count10)
  print(depth,"totbayes", "{:.3f}".format(pice) , "{:.3f}".format(pclass) , "{:.3f}".format(pice_given_class) , "{:.3f}".format(pclass_given_ice), "{:.3f}".format(csi), flush=True )

