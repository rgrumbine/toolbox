import os
import sys
import datetime
from math import *
import numpy as np
import numpy.ma as ma

import netCDF4

mom6 = netCDF4.Dataset("mom6/025/ocean_hgrid.nc", "r")
mom6_mask = netCDF4.Dataset("mom6/025/ocean_mask.nc", "r")

mom_nxp = len(mom6.dimensions['nxp'])
mom_nyp = len(mom6.dimensions['nyp'])
mom_x   = mom6.variables['x'][:,:]
mom_y   = mom6.variables['y'][:,:]
print(mom_y.max(), mom_y.min())
print(mom_x.max(), mom_x.min())

mask_nx = len(mom6.dimensions['nx'])
mask_ny = len(mom6.dimensions['ny'])
mom_mask = mom6_mask.variables['mask'][:,:]
print("mask max min ",mom_mask.max(), mom_mask.min() )



cice6 = netCDF4.Dataset("cice6/025/grid_cice_NEMS_mx025.nc", "r")
kmtu  = netCDF4.Dataset("cice6/025/kmtu_cice_NEMS_mx025.nc", "r")

ice_ni = len(cice6.dimensions['ni'])
ice_nj = len(cice6.dimensions['nj'])
ice_lat = cice6.variables['ulat'][:,:]
ice_lon = cice6.variables['ulon'][:,:]
ice_lat *= 180./pi
ice_lon *= 180./pi
print(ice_ni, ice_nj)
print(ice_lat.max(), ice_lat.min() )
print(ice_lon.max(), ice_lon.min() )
kmt = kmtu.variables['kmt'][:,:]

x0 = ice_lat - mom_y[2::2,2::2]

d = np.abs(x0)
toler = 1.e-5
mask = ma.masked_array(d > toler)
indices = mask.nonzero()
for k in range(0,len(indices[0])):
  j = indices[0][k]
  i = indices[1][k]
  print('lat ',i,j, ice_lon[j,i], ice_lat[j,i], mom_x[2+2*j,i*2+2], mom_y[2+2*j,i*2+2], x0[j,i] ) 

x0 = ice_lon - mom_x[2::2,2::2]
d = np.abs(x0)
toler = 1.e-5
mask = ma.masked_array(d > toler)
indices = mask.nonzero()
for k in range(0,len(indices[0])):
  j = indices[0][k]
  i = indices[1][k]
  print('lon ',i,j, ice_lon[j,i], ice_lat[j,i], mom_x[2+2*j,i*2+2], mom_y[2+2*j,i*2+2],  x0[j,i] ) 


# Is sub-ice cavity included?
imask = ma.masked_array(ice_lat < -77.5)
indices = imask.nonzero()
for k in range(0,len(indices[0])):
  j = indices[0][k]
  i = indices[1][k]
  print('mask ',i,j, ice_lon[j,i], ice_lat[j,i], mom_mask[j,i], kmt[j,i] )

# Intermediates?
#imask = ma.masked_array(mom_mask > 0)
#imask = ma.logical_and(imask, mom_mask < 1.0)
#imask = ma.masked_array(kmt > 0)
#imask = ma.logical_and(imask, kmt < 1.0)
imask = ma.masked_array( (kmt - mom_mask) != 0)
indices = imask.nonzero()
for k in range(0,len(indices[0])):
  j = indices[0][k]
  i = indices[1][k]
  print('intermed ',i,j, ice_lon[j,i], ice_lat[j,i], kmt[j,i], mom_mask[j,i] )


