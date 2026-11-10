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

#RG: read in from data file
print("starting",flush=True)
src = nc.Dataset(sys.argv[1],'r') 
src_lats_1d = src.variables['latitude'][:]
src_lons_1d = src.variables['longitude'][:]

# Append the 0-degree longitude slice as 360 degrees
src_lons_padded = np.append(src_lons_1d, 360.0)

# Create 2D coordinate mesh for the source grid
src_lon_2d, src_lat_2d = np.meshgrid(src_lons_padded, src_lats_1d)

# Pole value = average of highest latitudes
maxlat = src_lats_1d.max()
#debug: print("maxlat = ",maxlat)

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
#debug: print("target x",target_x_2d.max(), target_x_2d.min() )
#debug: print("target y",target_y_2d.max(), target_y_2d.min() )


# Inverse transform: stereographic (x, y) -> geographic (lon, lat)
target_lon_2d, target_lat_2d = transformer_to_geo.transform(target_x_2d, target_y_2d)
#debug: print('lat ',target_lat_2d.max(), target_lat_2d.min() )

# inputs are in [-180,180) translate to [0,360)
target_lon_2d[target_lon_2d < 0] += 360
#debug: print('lon ',target_lon_2d.max(), target_lon_2d.min() )

# Flatten coordinates for SciPy interpolation
points = np.column_stack((src_lon_2d.ravel(), src_lat_2d.ravel()))

# Target evaluation points
xi = (target_lon_2d, target_lat_2d)


# ---------------------------------------------------------
# 3. Interpolation
#------------- get data --------------------------------------------------------
# Append the 0-degree longitude slice as 360 degrees
for parm in 'ICEC', 'PRMSL':
  src_data = src.variables[parm][:,:]
  src_data_padded = np.concatenate([src_data, src_data[:, :1]], axis=1)
  #debug: print("src_data_padded",src_data_padded.max(), src_data_padded.min() )
  pole = src_data_padded[src_lat_2d == maxlat].sum() /  len(src_lons_padded)
  # ---------------------------------------------------------
  values = src_data_padded.ravel()
  
  # Linear interpolation onto target 2D Polar Stereographic grid
  target_data = griddata(points, values, xi, method="linear")
  
  #-------------------------------------------------------------------
  
  target_data[np.isnan(target_data)] = pole
  print(parm,'target results ',target_data.max(), target_data.min() )


src.close()
