import sys
import time

import netCDF4 as nc
import numpy as np
import pyproj
from scipy.interpolate import griddata

# ---------------------------------------------------------
# 1. Source: 2D Regular/Reduced Gaussian Grid
# ---------------------------------------------------------
# Example: 1D arrays defining Gaussian latitudes and regular longitudes
# (In real cases, extract lats/lons from your GRIB/NetCDF dataset)
#src_lats_1d = np.linspace(89.0, 50.0, 128)  # Northern hemisphere Gaussian lats
#src_lons_1d = np.linspace(0.0, 359.5, 256)   # 0 to 360 or -180 to 180

#RG: read in from data file
print("starting",flush=True)
src = nc.Dataset(sys.argv[1],'r') 
src_lats_1d = src.variables['latitude'][:]
src_lons_1d = src.variables['longitude'][:]

# Append the 0-degree longitude slice as 360 degrees
src_lons_padded = np.append(src_lons_1d, 360.0)

# Create 2D coordinate mesh for the source grid
#src_lon_2d, src_lat_2d = np.meshgrid(src_lons_1d, src_lats_1d)
# Build the padded coordinate mesh
src_lon_2d, src_lat_2d = np.meshgrid(src_lons_padded, src_lats_1d)

# Pole value = average of highest latitudes
maxlat = src_lats_1d.max()
#debug: print("maxlat = ",maxlat)
count = src_lat_2d[src_lat_2d == maxlat].sum()
#debug: print('count = ',count, count/maxlat, len(src_lons_padded) )

# ---------------------------------------------------------
# 2. Target: Polar Stereographic Grid Definition
# ---------------------------------------------------------
# Define target grid in projected coordinates (meters from pole)
# EPSG:3413 = WGS 84 / NSIDC Sea Ice Polar Stereographic North
# EPSG:3995 = WGS 84 / Arctic Polar Stereographic
proj_polar = pyproj.CRS("EPSG:3413")
proj_geo = pyproj.CRS("EPSG:4326")

transformer_to_geo = pyproj.Transformer.from_crs(proj_polar, proj_geo, always_xy=True)

# Define 2D regular grid in stereographic meters
nx, ny = 512, 512
dx = 25000 # meters
dx = 23800 # meters -- 1/16 bedient
x_1d = np.linspace(-nx/2*dx, nx/2*dx, nx)
y_1d = np.linspace(-ny/2*dx, ny/2*dx, ny)
target_x_2d, target_y_2d = np.meshgrid(x_1d, y_1d)
print("target x",target_x_2d.max(), target_x_2d.min() )
print("target y",target_y_2d.max(), target_y_2d.min() )


# Inverse transform: stereographic (x, y) -> geographic (lon, lat)
target_lon_2d, target_lat_2d = transformer_to_geo.transform(target_x_2d, target_y_2d)
print('lat ',target_lat_2d.max(), target_lat_2d.min() )

# Normalize target longitudes to match source convention (e.g., [0, 360))
#target_lon_2d = target_lon_2d % 360.0
#target_lon_2d = ((target_lon_2d + 180.0) % 360.0) - 180.0
# inputs are in [-180,180) translate to [0,360)
target_lon_2d[target_lon_2d < 0] += 360
print('lon ',target_lon_2d.max(), target_lon_2d.min() )

# ---------------------------------------------------------
# 3. Interpolation
# ---------------------------------------------------------
#------------- get data --------------------------------------------------------
# Append the 0-degree longitude slice as 360 degrees
src_data = src.variables['ICEC'][:,:]
src_data_padded = np.concatenate([src_data, src_data[:, :1]], axis=1)
print("src_data_padded",src_data_padded.max(), src_data_padded.min() )
pole = src_data_padded[src_lat_2d == maxlat].sum() /  len(src_lons_padded)
#debug: print('average = ',src_data_padded[src_lat_2d == maxlat].sum() /  len(src_lons_padded) )
#debug: sys.exit(0)
# ---------------------------------------------------------
# Flatten coordinates for SciPy interpolation
points = np.column_stack((src_lon_2d.ravel(), src_lat_2d.ravel()))
#values = src_data.ravel()
values = src_data_padded.ravel()

# Target evaluation points
xi = (target_lon_2d, target_lat_2d)

# Linear interpolation onto target 2D Polar Stereographic grid
target_data = griddata(points, values, xi, method="linear")

#-------------------------------------------------------------------

print('target results ',target_data.max(), target_data.min() )
print('isnans ',(np.isnan(target_data)).sum(), nx*ny )
print('lats ',target_lat_2d[np.isnan(target_data)])
print('lons ',target_lon_2d[np.isnan(target_data)])
print('where ',np.where(np.isnan(target_data)) )

target_data[np.isnan(target_data)] = pole
print('target results ',target_data.max(), target_data.min() )
