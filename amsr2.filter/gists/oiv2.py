import numpy as np
import netCDF4 as nc

# expects 'allmatches' -- vector of matchups -- to be present
# date management by 'tag8' (YYYYMMDD) 

#---------------------------------------------------------------
# Use SST from qdoi v2, including its sea ice cover
# Read sst analysis, add sst and analysis' ice conc to match (sst, ice_sst)

tag8='20240101'
sstbase='/u/robert.grumbine/static/oiv2/'
fname=sstbase+'oisst-avhrr-v02r01.'+tag8+'.nc'

#---------------------------------------------------------------
sstgrid = nc.Dataset(fname, 'r', format='NETCDF4')
sst_nlats = len(sstgrid.dimensions["lat"])
sst_nlons = len(sstgrid.dimensions["lon"])

sst = np.zeros((sst_nlats, sst_nlons))
ice_sst = np.zeros((sst_nlats, sst_nlons))
#anom = np.zeros((sst_nlats, sst_nlons))
#err  = np.zeros((sst_nlats, sst_nlons))

sst   = sstgrid.variables["sst"][0,0,:,:]
ice_sst   = sstgrid.variables["ice"][0,0,:,:]
#anom  = sstgrid.variables["anom"] [0,0,:,:]
#err   = sstgrid.variables["err"][0,0,:,:]
#---------------------------------------------------------------

for k in range(0,len(allmatches)):
  allmatches[k].add_oiv2(sst, ice_sst)
  #debug:
  allmatches[i].show()

