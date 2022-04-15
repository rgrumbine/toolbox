import os
import sys
from math import *
import numpy as np
import numpy.ma as ma

import netCDF4 

three_d = [ "so", "uo", "vo", "temp" ]
zcoord = [ "z_i", "z_l" ]

# For reading: -------------------------------------------
orig = netCDF4.Dataset(sys.argv[1], 'r')
ncat = 40
FillValue = 1e20

#After https://stackoverflow.com/questions/13936563/copy-netcdf-file-using-python
for name, var in orig.variables.items():
    #print(name, orig.variables[name][:].max(), orig.variables[name][:].min() )
    if (name in three_d):
      for level in range(0,ncat):
        mask = ma.masked_array(orig.variables[name][:,level,:,:] < FillValue)
        indices = mask.nonzero()
        print("  ",name,level,orig.variables[name][:,level,:,:].max(), 
                              orig.variables[name][:,level,:,:].min(),
              "sum ",orig.variables[name][:,level,:,:].sum(),   
              "avg ",orig.variables[name][:,level,:,:].sum()/float(len(indices[0])) )
