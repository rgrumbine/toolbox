import os
import sys
import copy

import numpy
import numpy.ma as ma

import netCDF4 

# For reading: -------------------------------------------
model1  = netCDF4.Dataset(sys.argv[1], 'r', format="NETCDF4")
model2  = netCDF4.Dataset(sys.argv[2], 'r', format="NETCDF4")

#After https://stackoverflow.com/questions/13936563/copy-netcdf-file-using-python
# dimensions of the file
#debug: print(model1.dimensions)
#debug: print(model2.dimensions)

#debug: for name, dim in model1.dimensions.items():
#debug:     print("debug -- dimensions: ",name, dim, flush=True)
#debug: for name, dim in model2.dimensions.items():
#debug:     print("debug -- dimensions: ",name, dim, flush=True)

# global attributes
#debug: for a in model1.ncattrs():
#debug:     print("attr1 ",a)
#debug: for a in model2.ncattrs():
#debug:     print("attr2 ",a)

name = 'aice'
a1 = model1.variables[name][0,:,:]
a2 = model2.variables[name][0,:,:]
lat = model1.variables['TLAT'][:]
lon = model1.variables['TLON'][:]

#debug: print(lat.max(), lon.max(), lat.min(), lon.min() )

delta = copy.deepcopy(a1)
delta -= a2
#debug: print("a1",a1.max(), a1.min())
#debug: print("a2",a2.max(), a2.min())
#debug: print("delta",delta.max(), delta.min())

dmask = ma.masked_array(delta != 0)
indices = dmask.nonzero()
print(len(indices), len(indices[0]), len(indices[1]) )
#debug: exit(0)

for k in range(0, len(indices[1])):
  i = indices[1][k]
  j = indices[0][k]
  print(i,j,lat[j,i], lon[j,i], a1[j,i], a2[j,i], delta[j,i])

