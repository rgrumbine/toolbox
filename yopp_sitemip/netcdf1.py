import os
import sys
import csv


import numpy as np
  
import pygrib
import netCDF4 as nc

    
#RG library (also wants ijpt, latpt, const)
from grid import *

#---------------- Utilities -------------------------
# Parse a string to a value, later to add a
def llparse(x, standard="null"):
  # start with labelled string
  if (x[-1] == 'N' or x[-1] == 'E'):
    tmp = float(x[0:-1])
  elif (x[-1] == 'S' or x[-1] == 'W'):
    tmp = -float(x[0:-1])
  # else assume it's a clean number
  else:
    tmp = float(x)
#RG: Would be a good idea to have the option of enforcing some longitude standards
  return tmp

#Define standards by the minimum allowed longitude, -360, -180, 0
def lon_standards(x, lonmin = -999., lonmax = 999.):
  tmp = x
  if (tmp < lonmin):
    while(tmp < lonmin):
      tmp += 360.
  if (tmp > lonmax):
    while (tmp > lonmax):
      tmp -= 360.
  return tmp


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

#exit(0)

#-------------------------------------------
#open grib for reading:
grbs = pygrib.open("gfs.t00z.sfluxgrbf000.grib2")
print("grbs = ",grbs)

# x is the short grib index line, extract names here
k = 0
snames = []
for x in grbs:
  print(x.shortName, x.name)
  snames.append(x.shortName)
  k += 1

print(len(snames))

#exit(0)

#fails: print("len(grbs) =",len(grbs))
    
grbs.seek(0)
k = 1
for grb in grbs:
  x = grb.values
  print(k, snames[k-1])

  # RG: Assumes that all grids in file are regular lat-lon and same size and shape as first field.
  if (k == 1):
    lats, lons = grb.latlons()
    #RG: Can we get variable names?
    dx = lons[:,1]-lons[:,2]
    dy = lats[1,:]-lats[2,:]
    firstlat = lats[0,0]
    firstlon = lons[0,0]
    delta_lat = dy[0]
    delta_lon = dx[0]
    nlon = lats.shape[1]
    nlat = lats.shape[0]
    print("grid spec ",nlon, nlat, delta_lon, delta_lat, firstlon, firstlat, dx, dy)
    print("dx max min: ",nlon, firstlon, delta_lon, dx.max(), dx.min(),dx.max() - dx.min() )
    print("dy max min: ",nlat, firstlat, delta_lat, dy.max(), dy.min(),dy.max() - dy.min() )
    #prep netcdf files with grid info, lat, lon grid

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
print("k = ",k)
