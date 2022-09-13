import os
import sys
import csv

import pygrib
    
#RG library (also wants ijpt, latpt, const)
from grid import *

#Local:
from utility import *

#-------------------------------------------
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

  #patch = name, lat, lon, flat, flon, i, j, irange, jrange
  #patches.append(name, lat, lon, flat, flon, i, j, irange, jrange)
  k += 1

npatches = k
fyopp.close()

#open netcdf files for writing (npatches worth)

#-------------------------------------------
#loop over time -- f000 to f240
#open grib for reading:
grbs = pygrib.open("gfs.t00z.sfluxgrbf000.grib2")
print("grbs = ",grbs)

z2 = get_ll_info(grbs) 

# x is the short grib index line, extract names here
#Do at time 0 only
k = 0
snames = []
for x in grbs:
  print(x.shortName, x.name)
  snames.append(x.shortName)
  k += 1

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
print("nvars = ",k)
