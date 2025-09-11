import sys
from math import *
import datetime
import numpy as np
import netCDF4 as nc

'''
rerun -- using pre-spliced and analyzed data
      -- an an algorithm already in hand
'''
#-------------------------------------------------------------
nmax = 41234567
#nmax = 112345
ary = np.zeros((nmax,6))
y   = np.zeros((nmax))

fin = open(sys.argv[1],"r")
count = 0
for line in fin:
#100.00   0.00   1.00 458.37  89.88 129.54  1 0.000
    words = line.split()
    # skip points sst filter would get
    if float(words[8]) > 275.15:
        continue
    #i,j,lat,lon,mean,sigma,count
    mean   = float(words[0])
    sigma  = float(words[1])
    ocount = float(words[2])
    scaled = float(words[3])
    tmean  = float(words[4])
    tsigma = float(words[5])
    ary[count,0] = mean
    ary[count,1] = sigma
    ary[count,2] = ocount
    ary[count,3] = scaled
    ary[count,4] = tmean
    ary[count,5] = tsigma

    if (float(words[9]) > 0 ):
        y[count] = 1
    else:
        y[count] = 0
    #regressor: y[count] = float(words[9])
    
    count += 1
    if (count >= nmax):
        break

print("count = ",count)
#-------------------------------------------------------------

allice = 0
pcount = 0
picount = 0

count00 = 0
count01 = 0
count10 = 0
count11 = 0
# Note that we're only concerned with points that satisfy this leaf's conditions
for i in range(0,count):
  if (y[i] > 0):
      allice += 1
  #if (ary[i,4] <= 265.761 and ary[i,4] > 225.656 and ary[i,3] > 42.849): 
  #if (ary[i,4] <= 265.761 and ary[i,4] > 218.670 and ary[i,5] < 22.832): 
  #  pcount += 1
  #  if (y[i] > 0):
  #    picount += 1
  #    count11 += 1
  #  else:
  #    count10 += 1
  #else:
  #  if (y[i] > 0):
  #    count01 += 1
  

  if (ary[i,4] <= 273.865):
    if (ary[i,0] > 86.985):
      if (ary[i,3] > 105.570):
        pcount += 1
        if (y[i] > 0):
          picount += 1
          count11 += 1
        else:
          count10 += 1
    else:
      if (ary[i,4] <= 268.525):
        pcount += 1
        if (y[i] > 0):
          picount += 1
          count11 += 1
        else:
          count10 += 1


pclass = float(pcount)/float(count) 
pice_given_class = count11/pcount
#print(pcount, allice, pclass, count11/allice, allice/count)


pice             = (count01 + count11)/pcount

if pice == 0:
  pclass_given_ice = 0
else:
  pclass_given_ice = pice_given_class * pclass / pice
csi = count11/(count11 + count01 + count10)

print("totbayes", "{:.3f}".format(pice) , "{:.3f}".format(pclass) , "{:.3f}".format(pice_given_class) , "{:.3f}".format(pclass_given_ice), "  {:.3f}".format(allice/count), flush=True )

