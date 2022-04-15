import os
import sys
import datetime
from math import *
import numpy as np
import numpy.ma as ma

import netCDF4

mom6 = netCDF4.Dataset("mom6/100/ocean_hgrid.nc", "r")

mom_nxp = len(mom6.dimensions['nxp'])
mom_nyp = len(mom6.dimensions['nyp'])
mom_x   = mom6.variables['x'][:,:]
mom_y   = mom6.variables['y'][:,:]

print(mom_y.max(), mom_y.min())

#mask = ma.masked_array(mom_x < 0)
#indices = mask.nonzero()
#print(indices[0], len(indices[0]))
#print(indices[1], len(indices[1]))
#for k in range(0,len(indices[0])):
#  j = indices[0][k]
#  i = indices[1][k]
#  mom_x[j, i] += 360.

print(mom_x.max(), mom_x.min())
#exit(0)
#netcdf ocean_hgrid {
#dimensions:
#	nyp = 641 ;
#	nxp = 721 ;
#	ny = 640 ;
#	nx = 720 ;
#	string = 255 ;
#variables:
#	char tile(string) ;
#	double y(nyp, nxp) ;
#		y:units = "degrees" ;
#	double x(nyp, nxp) ;
#		x:units = "degrees" ;
#	double dy(ny, nxp) ;
#		dy:units = "meters" ;
#	double dx(nyp, nx) ;
#		dx:units = "meters" ;
#	double area(ny, nx) ;
#		area:units = "m2" ;
#	double angle_dx(nyp, nxp) ;
#		angle_dx:units = "degrees" ;
#}


cice6 = netCDF4.Dataset("cice6/100/grid_cice_NEMS_mx100.nc", "r")

ice_ni = len(cice6.dimensions['ni'])
ice_nj = len(cice6.dimensions['nj'])
ice_lat = cice6.variables['ulat'][:,:]
ice_lon = cice6.variables['ulon'][:,:]
ice_lat *= 180./pi
ice_lon *= 180./pi
print(ice_ni, ice_nj)
print(ice_lat.max(), ice_lat.min() )
print(ice_lon.max(), ice_lon.min() )

x  = ice_lat - mom_y[2::2,:-1:2]
x0 = ice_lat - mom_y[2::2,2::2]
x1 = ice_lat - mom_y[1:-1:2,1::2]

d = np.abs(x0)
toler = 0.0001
mask = ma.masked_array(d > toler)
indices = mask.nonzero()
for k in range(0,len(indices[0])):
  j = indices[0][k]
  i = indices[1][k]
  print('lat ',i,j, ice_lon[j,i], ice_lat[j,i], mom_x[2+2*j,i*2+2], mom_y[2+2*j,i*2+2], x[j,i], x0[j,i], x1[j,i] ) 

x  = ice_lon - mom_x[2::2,:-1:2]
x0 = ice_lon - mom_x[2::2,2::2]
x1 = ice_lon - mom_x[1:-1:2,1::2]
d = np.abs(x0)
toler = 0.0001
mask = ma.masked_array(d > toler)
indices = mask.nonzero()
for k in range(0,len(indices[0])):
  j = indices[0][k]
  i = indices[1][k]
  print('lon ',i,j, ice_lon[j,i], ice_lat[j,i], mom_x[2+2*j,i*2+2], mom_y[2+2*j,i*2+2], x[j,i], x0[j,i], x1[j,i] ) 




#netcdf grid_cice_NEMS_mx100 {
#dimensions:
#	ni = 360 ;
#	nj = 320 ;
#variables:
#	double ulon(nj, ni) ;
#		ulon:units = "radians" ;
#		ulon:long_name = "Longitude of corner (Bu) points" ;
#	double ulat(nj, ni) ;
#		ulat:units = "radians" ;
#		ulat:long_name = "Latitude of corner (Bu) points" ;
#	double hte(nj, ni) ;
#		hte:units = "cm" ;
#		hte:long_name = "Distance between corner (Bu) points, east face" ;
#	double htn(nj, ni) ;
#		htn:units = "cm" ;
#		htn:long_name = "Distance between corner (Bu) points, north face" ;
#	double angle(nj, ni) ;
#		angle:units = "radians" ;
#		angle:long_name = "Angle at corner (Bu) points" ;
#	int kmt(nj, ni) ;
#		kmt:units = "none" ;
#		kmt:long_name = "ocean fraction at T-cell centers" ;
#// global attributes:
#		:history = "created on 20200822 from /scratch2/NCEPDEV/climate/Denise.Worthen/MOM6_FIX/100/ocean_hgrid.nc" ;
#}
