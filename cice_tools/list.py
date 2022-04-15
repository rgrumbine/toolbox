import os
import sys

import numpy
import netCDF4 

stresses = ["uvel", "vvel", "strocnxT", "strocnyT", "stressp_1", "stressp_2", "stressp_3", "stressp_4", "stressm_1", "stressm_2", "stressm_3", "stressm_4", "stress12_1", "stress12_2", "stress12_3", "stress12_4"]
categories = ["aicen", "vicen", "vsnon", "Tsfcn", "qsno001"]

# For reading: -------------------------------------------
orig  = netCDF4.Dataset(sys.argv[1], 'r')
ncat = 5

#After https://stackoverflow.com/questions/13936563/copy-netcdf-file-using-python
for name, var in orig.variables.items():

    #name = aicen, vicen, vvel, uvel, ...
    if name in categories:
      print(name, orig.variables[name][:].max(), orig.variables[name][:].min() )
      for k in range(0,ncat):
        print("  ",name,k,orig.variables[name][k,:,:].max(), orig.variables[name][k,:,:].min() )

k=0
name="aicen"
atot = orig.variables[name][k,:,:]
for k in range(1,ncat):
  atot += orig.variables[name][k,:,:]
  print("  ", name, k, atot.max(), atot.min(), atot.sum() )
print(name, atot.max(), atot.min(), atot.sum() )

name="qsno001"
name2="vsnon"
ratio = (orig.variables[name][k,:,:].min() /orig.variables[name2][k,:,:].max() ) #where name2 != 0
for k in range(0,ncat):
  print(name, k, orig.variables[name][k,:,:].min(), (orig.variables[name][k,:,:].min() /orig.variables[name2][k,:,:].max() )*(-1.e-6) )
 

# nilyr = 7 ;
# ncat = 5 ;
# nj = 1080 ;
# ni = 1440 ;
# 
# double qice001(ncat, nj, ni) ;
# double qice002(ncat, nj, ni) ;
# double qice003(ncat, nj, ni) ;
# double qice004(ncat, nj, ni) ;
# double qice005(ncat, nj, ni) ;
# double qice006(ncat, nj, ni) ;
# double qice007(ncat, nj, ni) ;
# double sice001(ncat, nj, ni) ;
# double sice002(ncat, nj, ni) ;
# double sice003(ncat, nj, ni) ;
# double sice004(ncat, nj, ni) ;
# double sice005(ncat, nj, ni) ;
# double sice006(ncat, nj, ni) ;
# double sice007(ncat, nj, ni) ;
