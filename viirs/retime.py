import sys
import time

import numpy as np
import numpy.ma as ma
import netCDF4 

from grid import *

#---------------------------------------------------------------------------
#Loop over input arg list (JRR-IceConcentration*)

#For output grid:
target_grid = global_5min()
tsumx  = np.zeros((target_grid.ny,target_grid.nx))
tsumx2 = np.zeros((target_grid.ny,target_grid.nx))
gcount = np.zeros((target_grid.ny,target_grid.nx),dtype=int)

n = 0
nvalid = 0
totnp = 0
ttot = 0

for fname in sys.argv[1:]:

  try:
    viirs = netCDF4.Dataset(fname, 'r')
  except:
    print("Could not open fname: ",fname,flush=True, file=sys.stderr)
    continue

  n += 1
  
  #This is a masked array, determined by fill value
  conc = viirs.variables['IceConc'][:,:]
  #debug: print(n,"conc ",conc.max(), conc.min(),flush=True, file=sys.stderr )
  indices = conc.nonzero()
  np = len(indices[0])
  if (np == 0):
      continue
  totnp += len(indices[0])

  #Geography:
  lats = viirs.variables['Latitude'][:,:]
  lons = viirs.variables['Longitude'][:,:]

  #Start Working:
  tstart = time.process_time()
  for k in range(0,len(indices[0])):
      i = indices[1][k]
      j = indices[0][k]
      # for gridding
      iloc = target_grid.inv_locate(lats[j,i],lons[j,i])
      ti = int(iloc[0]+0.5)
      if (ti == target_grid.nx):
        ti = 0
      tj = int(iloc[1]+0.5)
      gcount[tj,ti] += 1
      c = conc[j,i]
      tsumx[tj,ti]  += c
      tsumx2[tj,ti] += c*c
  dt = time.process_time() - tstart
  ttot += dt
  print("process ",len(indices[0]),'obs in ',dt ,'seconds',file=sys.stderr, flush=True)

print("number of files with valid ice conc: ",nvalid, file=sys.stderr)
print("total number of ice conc observations: ",totnp, file=sys.stderr)
print("total obs processing time: ",ttot, file=sys.stderr)

z = latpt()
cellcount = 0
mask = ma.masked_array(gcount > 0)
indices = mask.nonzero()
tstart = time.process_time()
for k in range(0,len(indices[0])):
    i = indices[1][k]
    j = indices[0][k]
    tsumx[j,i] /= gcount[j,i]
    tsumx2[j,i] = sqrt(max(0., tsumx2[j,i]/gcount[j,i] - tsumx[j,i]*tsumx[j,i]) )
    target_grid.locate(i,j,z)
    print(i,j,z.lat, z.lon, tsumx[j,i], tsumx2[j,i], gcount[j,i], flush=True, file=sys.stdout)
    cellcount += 1

print("gcount, avg: ",gcount.max(), gcount.min(), tsumx.max(), tsumx.min(), tsumx2.max(), tsumx2.min(),file=sys.stderr  )
print("cellcount = ",cellcount,file=sys.stderr)
print("writeout took ",time.process_time() - tstart, file=sys.stderr )

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
