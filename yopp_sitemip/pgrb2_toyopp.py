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
from grib_netcdf import *

#---------------------------------------------------------------
#pgrb2, pgrb2b Short Names to extract
snames = [ 'gh', 't', 'u', 'v', 'w', 'r' ]
#debug: print("short names being extracted on isobaric levels: ",snames, flush=True)


#open grib file for reading and initializing the netcdf:
cyc=sys.argv[1]
tag=sys.argv[2]

#This structure depends on date
#Newer:
#base="./gfs."+tag+"/"+cyc+"/atmos/"
#Older than: 
base="./gpfs/hps/nco/ops/com/gfs/prod/gfs."+tag

hh="000"
setup = False

# pgrb2, pgrb2b
f2 = base+"/gfs.t"+cyc+"z.pgrb2b.0p25.f"+hh
f1 = base+"/gfs.t"+cyc+"z.pgrb2.0p25.f"+hh
for fname in ( f1, f2):
  #debug print("fname = ",fname,flush=True)

  grbs = pygrib.open(fname)
  #debug print("grbs = ",grbs, flush=True)

  grbindex = pygrib.index(fname, 'shortName','typeOfLevel')
  #debug print('grib index keys:',grbindex.keys,flush=True)

  # RG: Assumes that all grids in file are regular lat-lon and same size 
  #     and shape as first field.
  if (not setup):
    z = get_ll_info(grbs)
    #debug print("llinfo = ",z, flush=True)


#---------------------------------------------------------------
# Work with the YOPP Site locations
  if (not setup):
    fyopp  = open("yopp_sites.csv","r")
    sreader = csv.reader(fyopp, delimiter=",")
    k = 0
    sites = []
    #open netcdf files for writing (npatches worth)
    for line in sreader:
      x = patches(z,line)
      sites.append(x)
      fout = sites[k].name+"_GFS_NCEP_pgrb_"+tag+cyc+".nc"
      sites[k].pncopen3(fout, tag, cyc);
    
      k += 1
    npatches = k
    fyopp.close()
    print("found ",npatches," patches to work with/on", len(sites) )

#----------------------------------------------------------------
#  Grid specified now and all patches opened up for writing
#----------------------------------------------------------------
#  Add the variables

  if (not setup):
    grbs.seek(0)
    k = 0
    for s in snames:
      print("short name = ",s, flush=True)
      select_grbs = grbindex(shortName = s, typeOfLevel='isobaricInhPa')
      for npatch in range(0,len(sites)):
        sites[npatch].addvar3(select_grbs[0])
    
      k += 1
    print(k," variables to work with/on", flush=True)

  setup = True
#  exit(0)
#----------------------------------------------------------------
  for ftime in range (0,121,1):
  #debug for ftime in range (0,2,1):
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
        #  grb.topLevel, grb.bottomLevel, grb.paramId, grb.forecastTime, flush=True)
      
        ## add to netcdf file
        if (grb.shortName in ishk):
          sname = grib_to_netcdf[grb.shortName][short_index]
          lname = grib_to_netcdf[grb.shortName][yopp_index]
        else:
          sname = grb.shortName
          lname = grb.name

        for patch in range(0,npatches):
          #debug print("k, patch = ",k,patch, flush=True)
          sites[patch].extractvar3(ftime, x, sname, grb.level)
  
      k += 1

#---------------------------------------------------------------
#close netcdf files
for k in range (0,len(sites)):
  sites[k].close()
