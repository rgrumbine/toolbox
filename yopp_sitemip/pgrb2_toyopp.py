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
#pgrb2 Short Names to extract
snames = [ 'gh', 't', 'u', 'v', 'w', 'r' ]
#debug: print('short names being extracted on isobaric levels: ",snames, flush=True)


#open grib file for reading and initializing the netcdf:
cyc=sys.argv[1]
tag=sys.argv[2]

#This structure depends on date
#Newer:
#base="./gfs."+tag+"/"+cyc+"/atmos/"
#Older than: 
base="./gpfs/hps/nco/ops/com/gfs/prod/gfs."+tag

hh="000"

fname = base+"/gfs.t"+cyc+"z.pgrb2.0p25.f"+hh
#debug print("fname = ",fname,flush=True)

grbs = pygrib.open(fname)
#debug print("grbs = ",grbs, flush=True)

grbindex = pygrib.index(fname, 'shortName','typeOfLevel')
#debug print('grib index keys:',grbindex.keys,flush=True)

# RG: Assumes that all grids in file are regular lat-lon and same size 
#     and shape as first field.
z = get_ll_info(grbs)
#debug print("llinfo = ",z, flush=True)

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
#Do at time 0 only -- nothing special about time 0 for the pgrb2 files
#
#Code experiment:
#grbs.seek(0)
#k = 0
#for s in snames:
#  print("short name = ",s, flush=True)
#  select_grbs = grbindex(shortName = s, typeOfLevel='isobaricInhPa')
#  k += 1
#print(k," variables to work with/on", flush=True)
#
#grbs.seek(0)
#k = 0
#for x in select_grbs:
#  #Verbose:
#  #verbose print(x.shortName, x.name, x.level, x.typeOfLevel, x.paramId, x.forecastTime, flush=True)
#  #verbose print(x, flush=True)
#  k += 1
#print("nvars = ",k, flush=True)
#
##coding experiment:
##sel2 = pygrib.index(fname,'shortName')
##print("sel2 = ",sel2,flush=True)
##s2 = sel2(shortName='gh')
##print("s2 = ",s2,flush=True)
#
##exit(0)

#----------------------------------------------------------------
#loop over time -- f000 to f120 by 1, 123 to 240 by 3
#for ftime in range (0,121,1):
#debug
for ftime in range (0,2,1):
  hh="{:03d}".format(ftime)
  fname = base+"/gfs.t"+cyc+"z.pgrb2.0p25.f"+hh
  grbs = pygrib.open(fname)
  grbindex = pygrib.index(fname, 'shortName', 'typeOfLevel')
  #debug print("grbs = ",grbs, flush=True)
  #debug print("grbindex = ",grbindex, flush=True)
  #debug print("hh, fname:",hh, fname, flush=True)

#Iterate over short names (list snames):
# gh = geopotential height
# t  = temperature
# r  = relative humidity -- what is wanted is q, specific humidity
# w  = vertical velocity Pa/s
# u  = U wind m/s
# v  = V wind

  grbs.seek(0)
  k = 1
  for short in snames:
    select_grbs = grbindex(shortName=short, typeOfLevel="isobaricInhPa") 
    for grb in select_grbs:
      x = grb.values
      #debug print(k, x.max(), x.min(), grb.level, grb.shortName, grb.name, 
      #debug grb.topLevel, grb.bottomLevel, grb.paramId, grb.forecastTime, flush=True)
    
      ## add to netcdf file
      for patch in range(0,npatches):
        #debug 
        print("k, patch = ",k,patch, flush=True)
      # 
      #   sites[patch].extractvar(ftime, x, grb.shortName) 
      #   sites[patch].addtime(ftime)
  
    k += 1

#---------------------------------------------------------------
#close netcdf files
for k in range (0,len(sites)):
  sites[k].close()
