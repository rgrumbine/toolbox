import sys
from math import *

import numpy as np
import numpy.ma as ma
import netCDF4 

from grid import *

#---------------------------------------------------------------------------
#Loop over input arg list (JRR-IceConcentration*)
#fname = "20220828/JRR-IceConcentration_v2r3_j01_s202208281036198_e202208281037426_c202208281059540.nc"

#For output grid:
target_grid = global_5min()
tsumx  = np.zeros((target_grid.ny,target_grid.nx))
tsumx2 = np.zeros((target_grid.ny,target_grid.nx))
gcount = np.zeros((target_grid.ny,target_grid.nx),dtype=int)
print("target grid dimensions",target_grid.ny,target_grid.nx)

n = 0
nvalid = 0
totnp = 0
# For histogram
counts = np.zeros((121),dtype=int)

for fname in sys.argv[1:]:
  #debug: print(n, fname,flush=True)

  try:
    viirs = netCDF4.Dataset(fname, 'r')
  except:
    print("Could not open fname: ",fname,flush=True)
    continue

  #debug: print("dimensions ",len(viirs.dimensions['Columns']), len(viirs.dimensions['Rows']) )
  n += 1
  
  #This is a masked array, determined by fill value
  conc = viirs.variables['IceConc'][:,:]
  print(n,"conc ",conc.max(), conc.min(),flush=True )
  indices = conc.nonzero()
  #debug: print("len indices:",len(indices), len(indices[0]), flush=True)
  np = len(indices[0])
  if (np == 0):
      continue
  totnp += len(indices[0])

  #Geography:
  lats = viirs.variables['Latitude'][:,:]
  lons = viirs.variables['Longitude'][:,:]

  #QC:

  #Start Working:
  for k in range(0,len(indices[0])):
      i = indices[1][k]
      j = indices[0][k]
      #verbose: print(lons[j,i], lats[j,i], conc[j,i], " pt")
      #conc histogram
      counts[int(conc[j,i]+0.5)] += 1
      # for gridding
      iloc = target_grid.inv_locate(lats[j,i],lons[j,i])
      ti = int(iloc[0]+0.5)
      if (ti == target_grid.nx):
        ti = 0
      tj = int(iloc[1]+0.5)
      gcount[tj,ti] += 1
      tsumx[tj,ti]  += conc[j,i]
      tsumx2[tj,ti] += conc[j,i]*conc[j,i]
      #debug print(j, i, tj, ti, lons[j,i], lats[j,i], conc[j,i], " pt", flush=True)
  #debug if (n > 300) :
  #debug break

print("number of files with valid ice conc: ",nvalid)
print("total number of ice conc observations: ",totnp)
print("Histogram: conc , # points")
for k in range(0,101):
    print(k,counts[k])
print(flush=True)

z = latpt()
cellcount = 0
mask = ma.masked_array(gcount > 0)
indices = mask.nonzero()
fout1 = open("fout1","w")
fout2 = open("fout2","w")

for k in range(0,len(indices[0])):
    i = indices[1][k]
    j = indices[0][k]
    tsumx[j,i] /= gcount[j,i]
    tsumx2[j,i] = sqrt(max(0., tsumx2[j,i]/gcount[j,i] - tsumx[j,i]*tsumx[j,i]) )
    target_grid.locate(i,j,z)
    if (gcount[j,i]/cos(pi*z.lat/180.) > 125.005 and tsumx[j,i] > 85.615 and tsumx2[j,i] < 9.855):
      print("grid ",i,j,z.lat, z.lon, tsumx[j,i], tsumx2[j,i], gcount[j,i], file=fout1)
    elif(gcount[j,i]/cos(pi*z.lat/180.) < 125.005 and gcount[j,i] < 14.5 and gcount[j,i]/cos(pi*z.lat/180.) > 23.1):
      print("grid ",i,j,z.lat, z.lon, tsumx[j,i], tsumx2[j,i], gcount[j,i], file=fout2)
    cellcount += 1

print("gcount, avg: ",gcount.max(), gcount.min(), tsumx.max(), tsumx.min(), tsumx2.max(), tsumx2.min()  )
print("cellcount = ",cellcount)

#write out netcdf of file
#open
#header (grid spec, ..)
#globals (time, producer, etc.)
#mean
#sqrt(var)
#count
#quality info
#
#close
