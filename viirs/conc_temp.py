import sys

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
csumx  = np.zeros((target_grid.ny,target_grid.nx))
csumx2 = np.zeros((target_grid.ny,target_grid.nx))
gcount = np.zeros((target_grid.ny,target_grid.nx),dtype=int)
print("target grid dimensions",target_grid.ny,target_grid.nx, file=sys.stderr)

n = 0
nvalid = 0
totnp = 0

for fname in sys.argv[1:]:
  #debug: print(n, fname,flush=True)

  try:
    viirs = netCDF4.Dataset(fname, 'r')
  except:
    print("Could not open fname: ",fname,flush=True, file=sys.stderr)
    continue

  #debug: print("dimensions ",len(viirs.dimensions['Columns']), len(viirs.dimensions['Rows']) )
  n += 1
  
  #This is a masked array, determined by fill value
  conc = viirs.variables['IceConc'][:,:]
  temp = viirs.variables['IceSrfTemp'][:,:] 
  print(n,"conc ",conc.max(), conc.min(),flush=True, file=sys.stderr )
  print(n,"temp ",temp.max(), temp.min(),flush=True, file=sys.stderr )
  indices = conc.nonzero()

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
      # for gridding
      iloc = target_grid.inv_locate(lats[j,i],lons[j,i])
      ti = int(iloc[0]+0.5)
      if (ti == target_grid.nx):
        ti = 0
      tj = int(iloc[1]+0.5)
      gcount[tj,ti] += 1
      c =  conc[j,i]
      csumx[tj,ti]  += c
      csumx2[tj,ti] += c*c
      t =  temp[j,i]
      tsumx[tj,ti]  += t
      tsumx2[tj,ti] += t*t
      #debug print(j, i, tj, ti, lons[j,i], lats[j,i], conc[j,i], t, " pt", flush=True)

print("number of files with valid ice conc: ",nvalid, file=sys.stderr)
print("total number of ice conc observations: ",totnp, file=sys.stderr)

z = latpt()
cellcount = 0
mask = ma.masked_array(gcount > 0)
indices = mask.nonzero()
for k in range(0,len(indices[0])):
    i = indices[1][k]
    j = indices[0][k]
    csumx[j,i] /= gcount[j,i]
    csumx2[j,i] = sqrt(max(0., csumx2[j,i]/gcount[j,i] - csumx[j,i]*csumx[j,i]) )
    tsumx[j,i] /= gcount[j,i]
    tsumx2[j,i] = sqrt(max(0., tsumx2[j,i]/gcount[j,i] - tsumx[j,i]*tsumx[j,i]) )
    target_grid.locate(i,j,z)
    print(i,j,z.lat, z.lon, csumx[j,i], csumx2[j,i], tsumx[j,i], tsumx2[j,i], gcount[j,i], flush=True, file=sys.stdout)
    cellcount += 1

print("gcount, avg: ",gcount.max(), gcount.min(), tsumx.max(), tsumx.min(), tsumx2.max(), tsumx2.min(),file=sys.stderr  )
print("cellcount = ",cellcount,file=sys.stderr)

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
