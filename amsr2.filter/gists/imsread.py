import os 
import sys
import numpy as np
import numpy.ma as ma
import netCDF4 as nc

import pyproj 

# IMS Map projection from projection:proj4 in netcdf header
proj4 = "+proj=stere +lat_0=90 +lat_ts=60 +lon_0=-80 +k=1 +x_0=0 +y_0=0 +a=6378137 +b=6356257 +units=m +no_defs" 

ims_base='/u/robert.grumbine/noscrub/imstmp/'
fname=ims_base+'ims2024001_4km_v1.3.nc'
ims = nc.Dataset(fname, 'r', format='NETCDF4')

nx = len(ims.dimensions["x"])
ny = len(ims.dimensions["y"])
#debug: print("nx ny ",nx, ny, flush=True)

ims_x = np.zeros((nx),dtype="float")
ims_y = np.zeros((ny),dtype="float")
ims_value = np.zeros((ny, nx),dtype="byte")

ims_x     = ims.variables["x"]     [:]
ims_y     = ims.variables["y"]     [:]
ims_value = ims.variables["IMS_Surface_Values"]  [0,:,:]
#debug: print("in reader ims ", ims_value[3245,2321], flush=True)
#debug: print(ims_value, flush=True)

#IMS_Surface_Values:comment = 
#  0: Outside Coverage Area, 
#  1: Open Water, 
#  2: Land Without Snow, 
#  3: Sea Ice or Lake Ice, 
#  4: Snow Covered Land" ;
#debug: print("ims max min ",ims_value.max(), ims_value.min() )
#debug: print("isproj?", pyproj.crs.is_proj(proj4)  )


pims = pyproj.Proj(proj4)
#debug: print("p = ",p)
#x = ims_x[int(nx/2)]
#y = ims_y[int(ny/2)]
#for i in range(0,ny):
#  r = p(x,ims_y[i],inverse=True)
#  #print(p(x,ims_y[i],inverse=True))  #tuple is lon, lat
#  print(i,r[0],r[1])

#(lons, lats) = p(ims_x,ims_y,inverse=True)
#print(lons.max(), lats.max(), ims_x[1]-ims_x[0], ims_y[1]-ims_y[0] )
#
#(lons, lats) = p(ims_y,ims_x,inverse=True)
#print(lons.max(), lats.max(), ims_x[1]-ims_x[0], ims_y[1]-ims_y[0] )
#print(len(lons))

## 12 min to brute force the locations
#lons = np.zeros((ny,nx))
#lats = np.zeros((ny,nx))
#for i in range(0,nx):
#  #debug: print("i = ",i,flush=True)
#  for j in range(0,ny):
#    r = p(ims_x[i], ims_y[j], inverse=True)
#    lons[j,i] = r[0]
#    lats[j,i] = r[1]
#
#debug: print(lons.max(), lats.max(), lons.min(), lats.min() )
#debug: print("x",ims_x.max() , ims_x.min() )

def ims_invlocate(proj, latitude, longitude):
  (x,y) = proj(longitude, latitude)
  fi = x/4000. + 6144./2.
  fj = y/4000. + 6144./2.
  i = int(fi+0.5)
  j = int(fj+0.5)
  return (i,j)

def is_land(ims, i, j, pm = 0):
  return (ims[j,i] == 2 or ims[j,i] == 4)
