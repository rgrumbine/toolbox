import sys
from math import *
import numpy as np
import netCDF4 as nc
import datetime


'''
rerun -- using pre-spliced and analyzed data
      -- an an algorithm already in hand


'''

#-------------------------------------------------------------
nmax = 41234567
#nmax = 112345
ary = np.zeros((nmax,6))
loc = np.zeros((nmax,2))
obs = np.zeros((nmax,2))
y   = np.zeros((nmax))
pred = np.zeros((nmax))

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

    loc[count,0] = float(words[6])
    loc[count,1] = float(words[7])
    obs[count,0] = float(words[8])
    obs[count,1] = float(words[9])

    if (float(words[9]) > 0 ):
        y[count] = 1
    else:
        y[count] = 0
    #regressor: y[count] = float(words[9])
    
    count += 1
    if (count >= nmax):
        break

#del loc obs
print("count = ",count)
#-------------------------------------------------------------

icount = 0
pcount = 0
picount = 0
for i in range(0,count):
  if (ary[i,4] <= 265.761 and ary[i,4] > 225.656 and ary[i,3] > 42.849): 
    pred[i] = 1
    pcount += 1
    if (y[i] > 0):
        picount += 1
  else:
    pred[i] = 0
  if (y[i] > 0):
    icount += 1

#del ary

pclass = float(pcount)/float(count) 
pice_given_class = picount/pcount
print(pcount, icount, count, pclass, pice_given_class)

# evaluate:
count00 = 0
count01 = 0
count10 = 0
count11 = 0
for i in range (0, count):
  if (pred[i] == 0 and y[i] == 0):
      count00 += 1
  if (pred[i] > 0 and y[i] > 0):
      count11 += 1
  if (pred[i] == 0 and y[i] > 0):
      count01 += 1
  if (pred[i] > 0 and y[i] == 0):
      count10 += 1

print("tot%correct ",count00, count01, count10, count11, (count00+count11)/(count00 + count01 + count10 + count11))

pice             = (count01 + count11)/count
print('pice, pice given class',pice, pice_given_class)

if pice == 0:
  pclass_given_ice = 0
else:
  pclass_given_ice = pice_given_class * pclass / pice
csi = count11/(count11 + count01 + count10)

print("totbayes", "{:.3f}".format(pice) , "{:.3f}".format(pclass) , "{:.3f}".format(pice_given_class) , "{:.3f}".format(pclass_given_ice), "{:.3f}".format(csi), flush=True )

