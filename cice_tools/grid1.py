import os
import sys
import datetime
from math import *
import numpy as np
import numpy.ma as ma

import netCDF4

mom6 = netCDF4.Dataset("mom6.nc", "r")
cice6 = netCDF4.Dataset("cice6.nc", "r")

mom_npts = len(mom6.dimensions['grid_size'])
mom_corn = len(mom6.dimensions['grid_corners'])
mom_center_lat = mom6.variables['grid_center_lat'][:]
mom_center_lon = mom6.variables['grid_center_lon'][:]
mask = ma.masked_array(mom_center_lon < 0)
indices = mask.nonzero()
for k in range(0,len(indices[0])):
  i = indices[0][k]
  mom_center_lon[i] += 360.


ice_npts = len(cice6.dimensions['grid_size'])
ice_corn = len(cice6.dimensions['grid_corners'])
ice_center_lat = cice6.variables['grid_center_lat'][:]
ice_center_lon = cice6.variables['grid_center_lon'][:]

#print(mom_npts, ice_npts)

x = (ice_center_lat - mom_center_lat)
#print('lat-delta ',x.max(), x.min())
#print('ice ',ice_center_lat.max(), ice_center_lat.min() )
#print('mom ',mom_center_lat.max(), mom_center_lat.min() )

y = np.abs(x)
mask = ma.masked_array(y > 0.001)
indices = mask.nonzero()
for k in range(0,len(indices[0])):
  i = indices[0][k]
  print(i,ice_center_lat[i], mom_center_lat[i], ice_center_lat[i] - mom_center_lat[i], ice_center_lon[i], mom_center_lon[i], ice_center_lon[i] - mom_center_lon[i])

#x = (ice_center_lon - mom_center_lon)
#print('lon-delta ',x.max(), x.min())
#print('ice ',ice_center_lon.max(), ice_center_lon.min() )
#print('mom ',mom_center_lon.max(), mom_center_lon.min() )

#netcdf cice6 {
#dimensions:
#grid_size = 1555200 ;
#grid_corners = 4 ;
#grid_rank = 2 ;
#ariables:
#int grid_dims(grid_rank) ;
#double grid_center_lat(grid_size) ;
#	grid_center_lat:units = "degrees" ;
#double grid_center_lon(grid_size) ;
#	grid_center_lon:units = "degrees" ;
#int grid_imask(grid_size) ;
#	grid_imask:units = "unitless" ;
#double grid_corner_lat(grid_size, grid_corners) ;
#	grid_corner_lat:units = "degrees" ;
#double grid_corner_lon(grid_size, grid_corners) ;
#	grid_corner_lon:units = "degrees" ;
