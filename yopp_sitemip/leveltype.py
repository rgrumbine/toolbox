import os
import sys
import csv
import datetime

import numpy as np
  
import pygrib
import netCDF4 as nc

#RG library (also wants ijpt, latpt, const)
#mmablib/py in PYTHONPATH
from grid import *

#Local utilities:
from utility import *
from patches import *

#---------------------------------------------------------------
#open grib for reading:
cyc="00"
tag="20210726"
base="./gfs."+tag+"/"+cyc+"/atmos/"

hh="001"
fname = base+"gfs.t"+cyc+"z.sfluxgrbf"+hh+".grib2"
print("fname = ",fname)
grbs = pygrib.open(base+"gfs.t"+cyc+"z.sfluxgrbf"+hh+".grib2")
print("grbs = ",grbs, flush=True)

# RG: Assumes that all grids in file are regular lat-lon and same size 
#     and shape as first field.
z = get_ll_info(grbs)

#---------------------------------------------------------------
# Work with the YOPP Site locations
fyopp  = open("loc4.csv","r")
sreader = csv.reader(fyopp, delimiter=",")
k = 0
sites = []
for line in sreader:
  x = patches(z,line)
  sites.append(x)
#open netcdf files for writing (npatches worth)
  fout = "patch"+"{:d}".format(k)
  sites[k].pncopen(fout, tag, cyc);

  k += 1

npatches = k
fyopp.close()
print("found ",npatches," patches to work with/on", len(sites) )


#----------------------------------------------------------------
#  Grid specified now and all patches opened up for writing
#----------------------------------------------------------------

#loop over time -- f000 to f120 by 1, 123 to 240 by 3
#for fhr in range (0,121,1):
#  hh="{:03d}".format(fhr)
#  fname = base+"gfs.t"+cyc+"z.sfluxgrbf"+hh+".grib2"
#  grbs = pygrib.open(base+"gfs.t"+cyc+"z.sfluxgrbf"+hh+".grib2")
#  print("grbs = ",grbs, flush=True)


#----------------------------------------------------------------
#Do at time 0 only
grbs.seek(0)
k = 0
for x in grbs:
  print(x.shortName, x.name, x.level, x.typeOfLevel, x.paramId)
  for npatch in range(0,len(sites)):
    sites[npatch].addvar(x)  #RG: need to check for successful addition of var
  k += 1
print("nvars = ",k, flush=True)

grbs.seek(0)
k = 1
for grb in grbs:
#for grb in grbs(typeOfLevel="depthBelowLandLayer"):
  x = grb.values
  print(k, x.max(), x.min(), grb.level, grb.shortName, grb.name, grb.topLevel, grb.bottomLevel, grb.paramId, flush=True)

  for patch in range(0,npatches):
    #y = x[5+patch:15+patch,3+patch:13+patch]
    #debug print("patch = ",patch, y, flush=True)
    # write to netcdf file
    sites[patch].extractvar(grb)
    #sites[patch].addtime

  k += 1

#close netcdf files
for k in range (0,len(sites)):
  sites[k].close()
