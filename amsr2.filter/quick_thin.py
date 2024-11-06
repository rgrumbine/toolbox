#!/u/robert.grumbine/env3.10/bin/python3
# python system
import os
import sys
import copy
from math import *
import datetime

# env libraries
import numpy as np
import numpy.ma as ma

#import netCDF4 as nc
#import pygrib
#import pyproj

# shared
from match import *
from filtering import *
from tools import *


start = datetime.datetime(2023,1,2)
end   = datetime.datetime(2023,3,31)
dt = datetime.timedelta(1)

"""
scan_thin: 
    read in a matchups file and 
    * ignore pts with ims not all same, and = 1 or 3
    * ignore pts with landmask != 0
    * ignore pts with posteriori != 174 or 165
    split to:
    ice-ice   (conc != 0 and ims = ' 3 3 3 3 3') -- correct
    ice-noice (conc != 0 and ims = ' 1 1 1 1 1') -- false
    noice-ice (conc == 0 and ims = ' 3 3 3 3 3') -- false
    noice-non (conc == 0 and ims = ' 1 1 1 1 1') -- correct
"""

def imsice(ims):
  if (ims[0] == 3 and 
      ims[1] == 3 and
      ims[2] == 3 and
      ims[3] == 3 and
      ims[4] == 3):
    return True
  else:
    return False

def imsopen(ims):
  if (ims[0] == 1 and 
      ims[1] == 1 and
      ims[2] == 1 and
      ims[3] == 1 and
      ims[4] == 1):
    return True
  else:
    return False
#----------------------------------------------------------

fin = open(sys.argv[1],"r")
f11 = open("f11", "w")
f10 = open("f10", "w")
f01 = open("f01", "w")
f00 = open("f00", "w")

post_use_vals = [165, 173, 174]

tb_lr = np.zeros((match.amsr2_lr.ntb))
tb_hr = np.zeros((match.amsr2_hr.ntb))

x = amsr2_lr(satid = 0, latitude = 0., longitude = 0.)
tmp = match.match(x)
  
allmatches = []

k = int(0)
ignore = int(0)
c11 = int(0)
c10 = int(0)
c01 = int(0)
c00 = int(0)
other = int(0)

for line in fin:
    tmp.lr_read(line)

    #Skip pts that are not cleanly cold ocean in land mask and posteriori file:
    if ((tmp.ice_land != 0) or (tmp.ice_post not in post_use_vals)):
        #debug: print(tmp.ice_land, tmp.ice_post)
        ignore += 1
        continue
   
    k += 1
    #Copy in to allmatches (for having everything in one array, not needed for 'thin'):
    #allmatches.append(tmp)
    #allmatches[k-1] = copy.deepcopy(tmp)
    if (k % 20000 == 0):
        print(tmp.obs.tb[5], tmp.icec, tmp.ice_post, tmp.ims)
        # Do this, but not f00 f11, because the errors are uncommon
        f10.flush()
        f01.flush()

    if (tmp.icec != 0 and imsice(tmp.ims) ):
        tmp.show(f11)
        c11 += 1
    elif (tmp.icec != 0 and imsopen(tmp.ims) ):
        tmp.show(f10)
        c10 += 1
    elif (tmp.icec == 0 and imsopen(tmp.ims) ):
        tmp.show(f00)
        c00 += 1
    elif (tmp.icec == 0 and  imsice(tmp.ims) ):
        tmp.show(f01)
        c01 += 1
    else:
        other += 1

fin.close()

print("ignore, other = ",ignore, other)
print('k = ',k)
print('stats ',c11, c10, c01, c00, c11+c01+c10+c00, 1.-(c11+c00)/(c11+c10+c01+c00) )
f11.close()
f01.close()
f10.close()
f00.close()
