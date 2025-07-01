import sys
import numpy as np
import pygrib
import netCDF4
import datetime


"""
run for each day

reader:
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
def bayes(tree, dr, ary, preds, pices, count):
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
        pices[ileaf] = 0.
      else:
        pice   = (count01 + count11)/tot
        pices[ileaf] = pice
        pclass = tot/count
        pice_given_class = count11/(count10+count11)
        pclass_given_ice = pice_given_class * pclass / pice
        csi = count11/(count11 + count01 + count10)
        print(ileaf,"leaf", "{:.3f}".format(pice) , "{:.3f}".format(pclass) , 
              "{:.3f}".format(pice_given_class) , "{:.3f}".format(pclass_given_ice), tot, tot/count,  "{:.3f}".format(pices[ileaf]), flush=True )


#--------------------------------------------------------------------------
countmax = 12123456
fmax = int(countmax / 5)
#fmax = 10000
ice = 20 
# ndarray to save for use in finding clusters
ary   = np.zeros((countmax,23))
pr    = np.zeros((countmax,6))
dr    = np.zeros((countmax,66+12))
grpr  = np.zeros((countmax,12))

from reader import *

count = 0
for mm in (1,2,3,4,5,6):
  tag = datetime.datetime(2025,mm,14)
  print(tag, flush=True)
  count = read(tag, ary, dr, count, fmax = fmax, countmax = countmax)

count = min(count, countmax)
print(count, " points to consider v countmax",countmax, flush=True)
#---------------------------------------------------------
# make categorical (int) for decision tree
x = ary[:count,20]*100
y = x.astype(dtype=np.int32)
# can actually run with just the percents as targets, but start with ice binary
for i in range(0,count):
  if (y[i] > 70):
    y[i] = 3
  elif (y[i] > 30):
    y[i] = 2
  elif (y[i] > 0):
    y[i] = 1
  else:
    y[i] = 0

import sklearn
from sklearn.tree import DecisionTreeClassifier

for depth in range(6,7):
  fout = open("fout."+"{:02d}".format(int(depth)), "w" )
  
  tree = DecisionTreeClassifier(max_depth = depth)
  tree.fit(dr[:count], y)
  preds = tree.predict(dr[:count])
  # want to do this only once; it's in bayes right now
  leaf = tree.apply(dr[:count])

  t     = sklearn.tree.export_text(tree, max_depth = 5)
  print("\ndepth, leaves",tree.get_depth(), tree.get_n_leaves() )
  print("decision tree top for depth ",depth,"\n",t)

  # check leaf behavior:
  pices = np.zeros((int(2**(depth+1))))
  bayes(tree, dr, ary, preds, pices, count)
  
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

  print("depth",depth, "tot%correct ",(count00+count11)/(count00 + count01 + count10 + count11))

  pice = (count01 + count11)/count
  pclass = (count10 + count11)/count
  pice_given_class = count11/(count10+count11)
  pclass_given_ice = pice_given_class * pclass / pice
  csi = count11/(count11 + count01 + count10)
  print(depth,"totbayes", "{:.3f}".format(pice) , "{:.3f}".format(pclass) , "{:.3f}".format(pice_given_class) , "{:.3f}".format(pclass_given_ice), "{:.3f}".format(csi), flush=True )

  # write out the augmented ary, 1-12,19-23, category, pice(category)
  for i in range(0, count):
    for k in range(0,12):
      print("{:6.2f}".format(ary[i, k]), end=" ", file=fout)
    for k in range(18,23):
      print("{:6.2f}".format(ary[i, k]), end=" ", file=fout)
    print("c {:d}".format(preds[i]) , end=" ", file=fout)
    print("{:.3f}".format(pices[leaf[i]]), file=fout)
  fout.close()
