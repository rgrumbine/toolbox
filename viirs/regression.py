import sys
from math import *
import numpy as np
import netCDF4 as nc
import datetime


'''
bring together the viirs l3 merge with the ims for that date and place

rerun -- using pre-spliced and analyzed data


'''

#-------------------------------------------------------------
tag = datetime.datetime(2025,6,19)
old = datetime.datetime(2024,12,31)
print(tag.toordinal()-old.toordinal())

ary = np.zeros((500000*9,4))
loc = np.zeros((500000*9,2))
obs = np.zeros((500000*9,2))
y   = np.zeros((500000*9))

fin = open(sys.argv[1],"r")
count = 0
for line in fin:
#100.00   0.00   1.00 458.37  89.88 129.54  1 0.000
    words = line.split()
    # skip points sst filter would get
    if float(words[6]) > 275.3:
        continue
    #i,j,lat,lon,mean,sigma,count
    mean = float(words[0])
    sigma = float(words[1])
    ocount = float(words[2])
    scaled = float(words[3])
    ary[count,0] = mean
    ary[count,1] = sigma
    ary[count,2] = ocount
    ary[count,3] = scaled

    loc[count,0] = float(words[4])
    loc[count,1] = float(words[5])
    obs[count,0] = float(words[6])
    obs[count,1] = float(words[7])
    #y[count] = float(words[8])
    y[count] = float(words[7])
    
    count += 1

print("count = ",count)
#-------------------------------------------------------------
def noop():
  return
#-----------------------------------------------------------------------
def bayes(tree, ary, y, preds, pices, count):
    leaf = tree.apply(ary[:count])
    for ileaf in range(0, int(leaf.max())+1 ):
      count00 = 0
      count01 = 0
      count10 = 0
      count11 = 0
      totice = 0
      for i in range (0, count):
        if (y[i] > 0):
            totice += 1
        if (leaf[i] == ileaf):
          if (preds[i] == 0 and y[i] == 0):
              count00 += 1
          if (preds[i] > 0 and y[i] > 0):
              count11 += 1
          if (preds[i] == 0 and y[i] > 0):
              count01 += 1
          if (preds[i] > 0 and y[i] == 0):
              count10 += 1
      tot    =  count00 + count01 + count10 + count11
      #debug: print('ileaf counts ',ileaf, tot, count00, count01, count10, count11)
      if (tot == 0):
        #debug: print("tot = 0!, ileaf = ",ileaf)
        noop()
      elif (count01+count11 == 0):
        print(ileaf, "no real ice in leaf ",tot, tot/count)
        pices[ileaf] = 0.
      else:
        pice   = totice/count
        pclass = tot/count
        pice_given_class = (count01+count11)/tot
        pices[ileaf] = pice_given_class

        if (pice == 0):
          pclass_given_ice = 0
        else:
          pclass_given_ice = pice_given_class * pclass / pice

        csi = count11/(count11 + count01 + count10)
        print(ileaf,"leaf", "{:.3f}".format(pice) , "{:.3f}".format(pclass) ,
              "{:.3f}".format(pice_given_class) , "{:.3f}".format(pclass_given_ice), tot, tot/count,  "{:.3f}".format(csi), flush=True )

#-------------------------------------------------------------
import sklearn
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor

for depth in range(1,4):
  #tree = DecisionTreeClassifier(max_depth = depth)
  tree = DecisionTreeRegressor(max_depth = depth)
  tree.fit(ary[:count], y[:count])
  preds = tree.predict(ary[:count])
  # want to do this only once; it's in bayes right now
  leaf = tree.apply(ary[:count])

  t     = sklearn.tree.export_text(tree, max_depth = 7, decimals = 3)
  print("\ndepth, leaves",tree.get_depth(), tree.get_n_leaves() )
  print("decision tree top for depth ",depth,"\n",t)
  importance = tree.feature_importances_
  for i, alpha in enumerate(importance):
    if alpha > 0:
      print("feature ",i,"importance ",alpha)

  # check leaf behavior:
  pices = np.zeros((int(2**(depth+1))))
  bayes(tree, ary, y, preds, pices, count)

  count00 = 0
  count01 = 0
  count10 = 0
  count11 = 0
  for i in range (0, count):
    if (preds[i] == 0 and y[i] == 0):
        count00 += 1
    if (preds[i] > 0 and y[i] > 0):
        count11 += 1
    if (preds[i] == 0 and y[i] > 0):
        count01 += 1
    if (preds[i] > 0 and y[i] == 0):
        count10 += 1

  print("depth",depth, "tot%correct ",count00, count01, count10, count11, (count00+count11)/(count00 + count01 + count10 + count11))

  pice   = (count01 + count11)/count
  pclass = 1
  pice_given_class = (count01+count11)/count

  if pice == 0:
    pclass_given_ice = 0
  else:
    pclass_given_ice = pice_given_class * pclass / pice
  csi = count11/(count11 + count01 + count10)
  print(depth,"totbayes", "{:.3f}".format(pice) , "{:.3f}".format(pclass) , "{:.3f}".format(pice_given_class) , "{:.3f}".format(pclass_given_ice), "{:.3f}".format(csi), flush=True )

  x = sklearn.feature_selection.r_regression(ary[:count,:], obs[:count,1])
  print("correlations ",x)

  # write out the used part of the ary, y, pice(leaf#)
#  fout = open("fout."+"{:02d}".format(int(depth)), "w" )
#  for i in range(0, count):
#    for k in range(0,4):
#      print("{:6.2f}".format(ary[i, k]), end=" ", file=fout)
#    print("{:7.3f}".format(loc[i,0]), "{:7.3f}".format(loc[i,1]),end=" ", file=fout)
#    print("{:6.2f}".format(obs[i,0]), "{:6.2f}".format(obs[i,1]), end=" ",file=fout)
#    print("{:2.0f}".format(y[i]), "{:5.3f}".format(pices[int(leaf[i])]), file=fout)
#  fout.close()

