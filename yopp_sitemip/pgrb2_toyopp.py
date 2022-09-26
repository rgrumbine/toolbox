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
#cyc="00"
#tag="20210726"
cyc=sys.argv[1]
tag=sys.argv[2]

#This structure depends on date
base="./gfs."+tag+"/"+cyc+"/atmos/"

hh="000"
fname = base+"gfs.t"+cyc+"z.pgrb2.0p25.f"+hh
print("fname = ",fname)
grbs = pygrib.open(fname)
print("grbs = ",grbs, flush=True)

# RG: Assumes that all grids in file are regular lat-lon and same size 
#     and shape as first field.
z = get_ll_info(grbs)
print("llinfo = ",z)

#exit(0)

#---------------------------------------------------------------
# Work with the YOPP Site locations
fyopp  = open("yopp_sites.csv","r")
sreader = csv.reader(fyopp, delimiter=",")
k = 0
sites = []
#open netcdf files for writing (npatches worth)
for line in sreader:
  x = patches(z,line)
  sites.append(x)
  #fout = "patch"+"{:d}".format(k) + "." + tag + cyc
  fout = sites[k].name+"_GFS_NCEP_"+tag+cyc+".nc"
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
  print(x.shortName, x.name, x.level, x.typeOfLevel, x.paramId, x.forecastTime, flush=True)
  print(x, flush=True)
  #for npatch in range(0,len(sites)):
  #  sites[npatch].addvar(x)  #RG: need to check for successful addition of var
  k += 1
print("nvars = ",k, flush=True)
exit(0)

#----------------------------------------------------------------
#loop over time -- f000 to f120 by 1, 123 to 240 by 3
for ftime in range (0,121,1):
#for ftime in range (0,2,1):
  hh="{:03d}".format(ftime)
  fname = base+"gfs.t"+cyc+"z.sfluxgrbf"+hh+".grib2"
  grbs = pygrib.open(base+"gfs.t"+cyc+"z.sfluxgrbf"+hh+".grib2")
  #debug print("grbs = ",grbs, flush=True)
  print("hh, fname:",hh, fname, flush=True)

  grbs.seek(0)
  k = 1
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
