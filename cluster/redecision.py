import sys
import numpy as np
import pygrib
import netCDF4
import datetime


"""
decision3.py: Write out only pts which are not pure water in depth 1 classifier

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
          if (preds[i] == 0 and ary[i,ice] == 0):
              count00 += 1
          elif (preds[i] > 0 and ary[i,ice] > 0):
              count11 += 1
          elif (preds[i] == 0 and ary[i,ice] > 0):
              count01 += 1
          elif (preds[i] > 0 and ary[i,ice] == 0):
              count10 += 1
      tot    =  count00 + count01 + count10 + count11
      if (tot == 0):
        noop()
      elif (count01+count11 == 0):
        print(ileaf, "no ice in leaf ",tot, tot/count)
        pices[ileaf] = 0.
      else:
        pice   = (count01 + count11)/tot
        pices[ileaf] = pice
        pclass = tot/count
        if (count10+count11 == 0):
          pice_given_class = 0
        else:
          pice_given_class = count11/(count10+count11)
        pclass_given_ice = pice_given_class * pclass / pice
        csi = count11/(count11 + count01 + count10)
        print(ileaf,"leaf", "{:.3f}".format(pice) , "{:.3f}".format(pclass) , 
              "{:.3f}".format(pice_given_class) , "{:.3f}".format(pclass_given_ice), tot, tot/count,  "{:.3f}".format(pices[ileaf]), flush=True )


#--------------------------------------------------------------------------
countmax = 14123456
fmax = countmax
#fmax = 10000
ice = 14
# ndarray to save for use in finding clusters
ary   = np.zeros((countmax,17))
dr    = np.zeros((countmax,66+12))

from reader import *

count = 0
fname = sys.argv[1]
count = reread(fname, ary, dr, count, fmax = countmax, countmax = countmax)

count = min(count, countmax)
print(count, " points to consider v countmax",countmax, flush=True)
#---------------------------------------------------------
# make categorical (int) for decision tree
x = ary[:count,ice]*100
y = x.astype(dtype=np.int32)
# can actually run with just the percents as targets, but start with ice binary
#for i in range(0,count):
#   if (y[i] > 0):
#       y[i] = 1
# slightly more complex -- WWIII critical points
#for i in range(0,count):
#  if (y[i] > 70):
#    y[i] = 3
#  elif (y[i] > 30):
#    y[i] = 2
#  elif (y[i] > 0):
#    y[i] = 1
#  else:
#    y[i] = 0

import sklearn
from sklearn.tree import DecisionTreeClassifier

for depth in range(1,2):
  fout = open("fout."+"{:02d}".format(int(depth)), "w" )
  
  tree = DecisionTreeClassifier(max_depth = depth)
  tree.fit(dr[:count], y)
  preds = tree.predict(dr[:count])
  # want to do this only once; it's in bayes right now
  leaf = tree.apply(dr[:count])

  t     = sklearn.tree.export_text(tree, max_depth = 7, decimals = 3)
  print("\ndepth, leaves",tree.get_depth(), tree.get_n_leaves() )
  print("decision tree top for depth ",depth,"\n",t)
  importance = tree.feature_importances_
  for i, alpha in enumerate(importance):
    if alpha > 0:
      print("feature ",i,"importance ",alpha)

  # check leaf behavior:
  pices = np.zeros((int(2**(depth+1))))
  bayes(tree, dr, ary, preds, pices, count)
  
  count00 = 0
  count01 = 0
  count10 = 0
  count11 = 0
  for i in range (0, count):
    if (preds[i] == 0 and ary[i,ice] == 0):
        count00 += 1
    elif (preds[i] > 0 and ary[i,ice] > 0):
        count11 += 1
    elif (preds[i] == 0 and ary[i,ice] > 0):
        count01 += 1
    elif (preds[i] > 0 and ary[i,ice] == 0):
        count10 += 1

  print("depth",depth, "tot%correct ",(count00+count11)/(count00 + count01 + count10 + count11))

  pice   = (count01 + count11)/count
  pclass = (count10 + count11)/count
  pice_given_class = count11/(count10+count11)
  pclass_given_ice = pice_given_class * pclass / pice
  csi = count11/(count11 + count01 + count10)
  print(depth,"totbayes", "{:.3f}".format(pice) , "{:.3f}".format(pclass) , "{:.3f}".format(pice_given_class) , "{:.3f}".format(pclass_given_ice), "{:.3f}".format(csi), flush=True )

  # write out the augmented ary
  for i in range(0, count):
    if (pices[leaf[i]] != 0):
      for k in range(0,17):
        print("{:6.2f}".format(ary[i, k]), end=" ", file=fout)
      print("",file=fout)
  fout.close()
