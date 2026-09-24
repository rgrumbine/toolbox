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
data = fin.variables['ICEC'][:,:]
#data = fin.variables['ICEC_surface'][0,:,:]
fin.close()

nx = len(lons)
ny = len(lats)
#debug: 
dl = lats[1:] - lats[0:-1]
#debug: 
print("dl ",dl.max(), dl.min() )
#debug: 
print("data ",data.max(), data.min(), data.sum()/nx/ny, flush=True )
#debug: print("histogram ",np.histogram(data, bins=[-5.e19,-1,0,0.5,1,1.01,1.e19]), flush=True)

#debug: sys.exit(0)
#------------------------------------------------
#domain = 0
#x = globe()
#proj = ccrs.PlateCarree()
domain = 1
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
title = sys.argv[2]
cb.set_label(title, fontsize=12)

plt.savefig("scalar."+f"{domain:d}"+".png")
plt.close()

#-----------------------------------------------
# geotiff -- framed by gemini
import rasterio
from rasterio.transform import from_origin
from scipy.interpolate import griddata

lons2d = np.zeros((ny, nx))
lats2d = np.zeros((ny, nx))
lons2d, lats2d = np.meshgrid(lons, lats)

grid_size = 1./12.

latmin, latmax = lats.min(), lats.max()
#debug: print('dlat = ',(latmax - latmin)/ny)
lonmin, lonmax = lons.min(), lons.max()
#debug: print('dlon = ',(lonmax - lonmin)/nx)
if (lonmax > 180+grid_size/2.):
    lons2d[lons2d > 180+grid_size/2.] -= 360.
#debug: lonmin, lonmax = lons.min(), lons.max()
#debug: print('dlon = ',(lonmax - lonmin)/nx)

tmplon = np.arange(-180.+grid_size/2., 180. , grid_size)
tmplat = np.arange(-90+grid_size/2., 90 + grid_size/2. , grid_size)
grid_lon, grid_lat = np.meshgrid(tmplon, tmplat)
#debug: print("gridlon shape",grid_lon.shape)
#debug: print("lats2d shape",lats2d.shape)
#debug: print("data shape",data.shape)

#sys.exit(0)

# 3. Interpolate points onto the regular grid
# Use 'nearest' or 'linear' depending on your point density
grid_val = griddata(
    (lons2d.ravel(), lats2d.ravel()), data.ravel(), (grid_lon, grid_lat), method='linear'
)
# Flip along the Y-axis so the top row corresponds to the northernmost latitude
grid_val = np.flipud(grid_val)

# 4. Define the Spatial Reference System and Affine Transform
# EPSG:4326 is standard WGS84 (Lat/Lon)
crs = 'EPSG:4326'
transform = from_origin(lonmin, latmax, grid_size, grid_size)

# 5. Write to GeoTIFF
with rasterio.open(
    'output.tif',
    'w',
    driver='GTiff',
    height=grid_val.shape[0],
    width=grid_val.shape[1],
    count=1,
    #dtype=grid_val.dtype,
    dtype=np.float32,
    crs=crs,
    transform=transform,
    nodata=-9999
) as dst:
    dst.write(np.nan_to_num(grid_val, nan=-9999), 1)
