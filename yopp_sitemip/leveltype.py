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
#open grib file for reading and initializing the netcdf:
cyc="00"
tag="20210726"
base="./gfs."+tag+"/"+cyc+"/atmos/"

# Use hr 001 as it has more variables than hr 000
hh="001"
fname = base+"gfs.t"+cyc+"z.sfluxgrbf"+hh+".grib2"
print("fname = ",fname)
grbs = pygrib.open(base+"gfs.t"+cyc+"z.sfluxgrbf"+hh+".grib2")
#debug print("grbs = ",grbs, flush=True)

# RG: Assumes that all grids in file are regular lat-lon and same size 
#     and shape as first field.
z = get_ll_info(grbs)

#---------------------------------------------------------------
# Work with the YOPP Site locations
fyopp  = open("loc4.csv","r")
sreader = csv.reader(fyopp, delimiter=",")
k = 0
sites = []
#open netcdf files for writing (npatches worth)
for line in sreader:
  x = patches(z,line)
  sites.append(x)
  fout = "patch"+"{:d}".format(k)
  sites[k].pncopen(fout, tag, cyc);

  k += 1

npatches = k
fyopp.close()
print("found ",npatches," patches to work with/on", len(sites) )

#----------------------------------------------------------------
#  Grid specified now and all patches opened up for writing
#----------------------------------------------------------------
#  Add the variables
#Do at time 0 only
grbs.seek(0)
k = 0
for x in grbs:
  #debug print(x.shortName, x.name, x.level, x.typeOfLevel, x.paramId, x.forecastTime)
  #debug print(x)
  for npatch in range(0,len(sites)):
    sites[npatch].addvar(x)  #RG: need to check for successful addition of var
  k += 1
print("nvars = ",k, flush=True)

#----------------------------------------------------------------
#loop over time -- f000 to f120 by 1, 123 to 240 by 3
#for ftime in range (0,121,1):
#  hh="{:03d}".format(ftime)
#  fname = base+"gfs.t"+cyc+"z.sfluxgrbf"+hh+".grib2"
#  grbs = pygrib.open(base+"gfs.t"+cyc+"z.sfluxgrbf"+hh+".grib2")
#debug print("grbs = ",grbs, flush=True)

grbs.seek(0)
k = 1
ftime = int(hh)
for grb in grbs:
#for grb in grbs(typeOfLevel="depthBelowLandLayer"):
  x = grb.values
  #debug print(k, x.max(), x.min(), grb.level, grb.shortName, grb.name, 
  #       grb.topLevel, grb.bottomLevel, grb.paramId, grb.forecastTime, flush=True)

  # add to netcdf file
  for patch in range(0,npatches):
    #debug print("k, patch = ",k,patch, flush=True)

    sites[patch].extractvar(ftime, x, grb.shortName) 
    #sites[patch].addtime(ftime)

  k += 1

#---------------------------------------------------------------
#close netcdf files
for k in range (0,len(sites)):
  sites[k].close()
