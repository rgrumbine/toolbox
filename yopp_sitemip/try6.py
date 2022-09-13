import os
import sys
import csv
import datetime

import numpy as np
  
#import pygrib
#wcoss2:
import ncepgrib2 as pygrib
import netCDF4 as nc

#RG library (also wants ijpt, latpt, const)
#mmablib/py in PYTHONPATH
from grid import *

#Local utilities:
from utility import *

#---------------------------------------------------------------
# Work with the YOPP Site locations
fyopp  = open("loc4.csv","r")

nx = 3072
ny = 1536
delta_lat  = -180./ny
delta_lon  =  360./nx
firstlon = 0.0
firstlat = 90.-delta_lat/2.
z = llgrid(nx = nx, ny = ny, dlat = delta_lat, dlon = delta_lon, firstlon = firstlon, firstlat = firstlat)

idelta_lat = 1./delta_lat
idelta_lon = 1./delta_lon
range_x = int(abs(1./delta_lon)+1.5)
range_y = int(abs(1./delta_lat)+1.5)
print("ranges = ",range_x, range_y)

sreader = csv.reader(fyopp, delimiter=",")
k = 0
for line in sreader:
  name = str.strip(line[0])
  slat = line[1]
  slon = line[2]
  lat  = llparse(slat)
  lon  = llparse(slon)
  # want range to be 1 degree
  flat = max(-90.,lat - 1.0)
  flon = lon-1.
  #debug print(k,slat, slon, lat, lon, flat, flon, z.inv_locate(flat, flon), flush=True )
  (i,j) = z.inv_locate(flat, flon)

  #patch = name, lat, lon, flat, flon, i, j, range_x, range_y
  #patches.append(name, lat, lon, flat, flon, i, j, range_x, range_y)
  #RG: make patches class
  k += 1

npatches = k
fyopp.close()
print("found ",npatches," patches to work with/on")

#---------------------------------------------------------------

#open netcdf files for writing (npatches worth)
for k in range(0,npatches):
  fout = "patch"+"{:d}".format(k)
  #debug print(k, "fout = ",fout,flush=True)
  #netcdf openpatch

#exit(0)

#---------------------------------------------------------------
#loop over time -- f000 to f240
#open grib for reading:
cyc="00"
tag="20210726"
base="./gfs."+tag+"/"+cyc+"/atmos/"

for fhr in range (0,121,1):
#for fhr in range (123,240,3):
  hh="{:03d}".format(fhr)
  #debug print("hh = ",hh, flush=True)

#debug exit(0)

hh="001"
fname = base+"gfs.t"+cyc+"z.sfluxgrbf"+hh+".grib2"
print("fname = ",fname)

fname="gfs/gfs.t00z.sfluxgrbf"+hh+".grib2"
grbs = pygrib.open(fname)
print("grbs = ",grbs, flush=True)

#debug exit(0)
# RG: Assumes that all grids in file are regular lat-lon and same size 
#     and shape as first field.

z2 = get_ll_info(grbs)


# x is the short grib index line, extract names here
#Do at time 0 only
grbs.seek(0)
k = 0
snames = []
for x in grbs:
  print(x.shortName, x.name)
  snames.append(x.shortName)
  k += 1
print("nvars = ",k, flush=True)

grbs.seek(0)
k = 1
for grb in grbs:
  x = grb.values
  print(k, snames[k-1])

  #replace alpha with actual ij starting points and ranges
  for patch in range(0,npatches):
    y = x[5+patch:15+patch,3+patch:13+patch]
    print("patch = ",patch, y)
    # find grib name -- x.shortName
    # translate grib name to netcdf name -- dictionary
    # write to netcdf file

  #debug print(k, x.max(), x.min(), flush=True )
  k += 1

#close netcdf files
