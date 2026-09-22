import sys

import numpy as np
import netCDF4 as nc

import matplotlib
import matplotlib.pyplot as plt


import cartopy.crs as ccrs
import cartopy.feature as cfeature

from regions import *

matplotlib.use('agg')
#------------------------------------------------
fin = nc.Dataset(sys.argv[1],'r')
lats = fin.variables['latitude'][:]
lons = fin.variables['longitude'][:]
fin.close()

fcst = nc.Dataset(sys.argv[2], 'r')
data = fcst.variables['ICEC'][:,:]
fcst.close()

nx = len(lons)
ny = len(lats)
dl = lats[1:] - lats[0:-1]
print("dl ",dl.max(), dl.min() )
print("data ",data.max(), data.min(), data.sum()/nx/ny )
print("histogram ",np.histogram(data, bins=[-5.e19,-1,0,1,1.01,1.e19]))
print("datasq ",data.max()**2, data.min()**2 )

#debug: sys.exit(0)
#------------------------------------------------
domain = 1
#0: x = globe()
#proj = ccrs.PlateCarree()
x = nh()
proj = ccrs.NorthPolarStereo(central_longitude = x.central_longitude)

#--------------------------------------------------
ax  = plt.axes(projection = proj)
fig = plt.figure(figsize = x.figsize)
ax  = fig.add_subplot(1,1,1, projection = proj)

cmap = matplotlib.colormaps.get_cmap('jet')

xlocs = x.xlocs
ylocs = x.ylocs
ax.set_extent(x.extent, crs=ccrs.PlateCarree() )

proj = ccrs.PlateCarree()
ax.coastlines(resolution='10m')
ax.gridlines(crs = proj, xlocs = xlocs, ylocs = ylocs)

cmap = matplotlib.colormaps.get_cmap('jet')
cs = ax.pcolormesh(lons, lats, data,
                         cmap = cmap,
                         transform= proj )
cb = plt.colorbar(cs, extend='both', orientation='horizontal', shrink=0.5, pad=.04)
title = sys.argv[3]
cb.set_label(title, fontsize=12)

plt.savefig("scalar."+f"{domain:d}"+".png")
plt.close()
