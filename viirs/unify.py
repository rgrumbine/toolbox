import sys
from math import *
import numpy as np
import netCDF4 as nc
import datetime


'''
bring together the viirs l3 merge with the ims for that date and place



'''

#-------------------------------------------------------------
tag = datetime.datetime(2025,6,19)
old = datetime.datetime(2024,12,31)
print(tag.toordinal()-old.toordinal())

ary = np.zeros((500000,4))
y   = np.zeros((500000))

analy = nc.Dataset(sys.argv[1])
ims = analy.variables['IMS_Surface_Values'][0,:,:]
#1 = open water
#3 = sea or lake ice

fin = open(sys.argv[2],"r")
count = 0
for line in fin:
    words = line.split()
    #i,j,lat,lon,mean,sigma,count
    i = int(words[0])
    j = int(words[1])
    ice = ims[j,i]
    if (ice == 1):
        ice = 0
    elif (ice == 3):
        ice = 1
    else:
        continue
    lat = float(words[2])
    if (lat < 20):
        continue
    lon = float(words[3])
    mean = float(words[4])
    sigma = float(words[5])
    ocount = float(words[6])
    #ary[count,0] = float(i)
    #ary[count,1] = float(j)
    #ary[count,0] = lat
    #ary[count,1] = lon
    ary[count,0] = mean
    ary[count,1] = sigma
    ary[count,2] = ocount
    ary[count,3] = ocount / cos(pi*lat/180.)
    y[count] = ice
    
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

for depth in range(1,5):
  tree = DecisionTreeClassifier(max_depth = depth)
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
    if (preds[i] == 0 and ary[i,ice] == 0):
        count00 += 1
    if (preds[i] > 0 and ary[i,ice] > 0):
        count11 += 1
    if (preds[i] == 0 and ary[i,ice] > 0):
        count01 += 1
    if (preds[i] > 0 and ary[i,ice] == 0):
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


