import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
  
import pygrib

#from mpl_toolkits.basemap import Basemap
#from mpl_toolkits.basemap import shiftgrid
    
#RG library (also wants ijpt, latpt, const)
from grid import *

#open for reading:
grbs = pygrib.open("gfs.t00z.sfluxgrbf000.grib2")
print("grbs = ",grbs)
#fails: print("len(grbs) =",len(grbs))
    
grbs.seek(0)
k = 1
for grb in grbs:
  #print(grb, flush=True)
  x = grb.values
  #print(x.max(), x.min(), flush=True)
  #print("x = ",x, flush=True)

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
    print("dx max min: ",nlon, firstlon, delta_lon, dx.max(), dx.min(),dx.max() - dx.min() )
    print("dy max min: ",nlat, firstlat, delta_lat, dy.max(), dy.min(),dy.max() - dy.min() )
    z = llgrid(nx = nlon, ny = nlat, dlat = delta_lat, dlon = delta_lon, firstlon = firstlon, firstlat = firstlat)

  y = x[5:15,3:13]
  print("y = ",y)

  #print(k, x.max(), x.min(), flush=True )
  k += 1

print("k = ",k)
