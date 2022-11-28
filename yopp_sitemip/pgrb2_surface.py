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

# this version works on the surface variables and outputs them blindly under grib2 short names
usehk = False

surface_vars = [ "vis", "gust", "hindex", "sp", "orog", "t", "sdwe", "sde", "cpofp", "wilt", "fldcp", "SUNSD", "lftx", "cape", "cin", "4lftx", "hpbl", "lsm", "ci", "landn" ]

unknown_lev_vars=[ "pwat" , "cwat"] 

#---------------------------------------------------------------
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
  snames = []
  #debug print("fname = ",fname,flush=True)

  grbs = pygrib.open(fname)
  #debug print("grbs = ",grbs, flush=True)
  #debug for x in grbs:
  #  print(x.shortName, x.typeOfLevel)


  #grbindex = pygrib.index(fname, 'shortName','typeOfLevel')
  grbindex = pygrib.index(fname, 'typeOfLevel')
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
      fout = sites[k].name+"_GFS_NCEP_pgrb_surf_"+tag+cyc+".nc"
      sites[k].pncopen(fout, tag, cyc);
    
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
    select_grbs = grbindex(typeOfLevel='surface')
    for x in select_grbs:
      if (x.shortName in surface_vars):
        print("selected: ",x.shortName, x.typeOfLevel, flush=True)
        snames.append(x.shortName)
        for npatch in range(0,len(sites)):
          sites[npatch].addvar(x, usehk=usehk)
        k += 1

    select_grbs = grbindex(typeOfLevel='unknown')
    for x in select_grbs:
      if (x.shortName == 'pwat' or x.shortName == 'cwat'):
        print("selected: ",x.shortName, x.typeOfLevel, flush=True)
        for npatch in range(0,len(sites)):
          sites[npatch].addvar(x, usehk=usehk)
        snames.append(x.shortName)
        k += 1
  
  print(k," variables to work with/on", flush=True)
  print("length of snames ",len(snames), flush=True)

  setup = True

  #debug exit(0)
#----------------------------------------------------------------
  for ftime in range (0,121,1):
  #debug for ftime in range (0,2,1):
    hh="{:03d}".format(ftime)
    fname = base+"/gfs.t"+cyc+"z.pgrb2.0p25.f"+hh
    grbs = pygrib.open(fname)
    grbindex = pygrib.index(fname, 'typeOfLevel')
    #debug print("grbs = ",grbs, flush=True)
    #debug print("grbindex = ",grbindex, flush=True)
    #debug print("hh, fname:",hh, fname, flush=True)
  
    grbs.seek(0)
    k = 1
    select_grbs = grbindex(typeOfLevel="surface") 
    for grb in select_grbs:
      if (grb.shortName in surface_vars):
        x = grb.values
        #debug print(k, x.max(), x.min(), grb.level, grb.shortName, grb.name, 
        #debug   grb.topLevel, grb.bottomLevel, grb.paramId, grb.forecastTime, flush=True)
      
        ## add to netcdf file
        sname = grb.shortName
        lname = grb.name

        for patch in range(0,npatches):
          #debug print("k, patch = ",k,patch, flush=True)
          sites[patch].extractvar(ftime, x, sname)
        k += 1

    select_grbs = grbindex(typeOfLevel="unknown") 
    for grb in select_grbs:
      if (grb.shortName == 'pwat' or grb.shortName == 'cwat'):
        x = grb.values
        #debug print(k, x.max(), x.min(), grb.level, grb.shortName, grb.name, 
        #debug   grb.topLevel, grb.bottomLevel, grb.paramId, grb.forecastTime, flush=True)
        ## add to netcdf file
        sname = grb.shortName
        lname = grb.name
        for patch in range(0,npatches):
          #debug print("k, patch = ",k,patch, flush=True)
          sites[patch].extractvar(ftime, x, sname)
        k += 1

#---------------------------------------------------------------
#close netcdf files
for k in range (0,len(sites)):
  sites[k].close()
