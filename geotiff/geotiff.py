import numpy as np
import netCDF4 as nc

import rasterio
from rasterio.transform import from_origin

# 1. Create a sample 2D data array 
width, height = 4320, 2160
file = nc.Dataset("a.nc","r")
data = file.variables['ICEC_meansealevel'][0,:,:]
#data = np.arange(width * height, dtype=np.float32).reshape((height, width))
print(data.max(), data.min() )

# 2. Define spatial reference parameters
# - Top-left origin coordinates (X, Y) in your map units (e.g., longitude/latitude or meters)
west, north = 0.0, 90.-1./24

# - Pixel resolution (cell size in X and Y directions)
pixel_size_x, pixel_size_y = 1./12, 1./12

# - Build the affine transform matrix
transform = from_origin(west, north, pixel_size_x, pixel_size_y)
print(transform)

# - Coordinate Reference System (WGS 84 / EPSG:4326)
crs = "EPSG:4326"

# 3. Write data to a GeoTIFF
output_filename = "output.tif"

with rasterio.open(
    output_filename,
    "w",
    driver="GTiff",
    height=height,
    width=width,
    count=1,  # Number of bands
    dtype=data.dtype,  # Data type (e.g., float32, uint8)
    crs=crs,
    transform=transform,
#    nodata=9.999e+20,  # Optional: set a NoData value
) as dst:
    # Write the 2D array to Band 1
    dst.write(data, 1)

print(f"Successfully saved GeoTIFF to {output_filename}")
