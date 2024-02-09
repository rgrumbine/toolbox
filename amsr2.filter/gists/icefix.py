import os 
import sys
import numpy as np
import numpy.ma as ma
import netCDF4 as nc

#def read_icefix(ice_longitude, ice_latitude, ice_distance, ice_land, ice_post, fname='seaice_fixed_fields.nc') :
fname='seaice_fixed_fields.nc'
icefix = nc.Dataset(fname, 'r', format='NETCDF4')

nlats = len(icefix.dimensions["nlats"])
nlons = len(icefix.dimensions["nlons"])
new_shape = (nlats, nlons)
#debug: print("nlon nlat ",nlons, nlats, flush=True)

#ice_longitude.resize(new_shape, refcheck=False)
ice_longitude = np.zeros((nlats, nlons),dtype="double")
ice_latitude = np.zeros((nlats, nlons),dtype="double")
ice_distance = np.zeros((nlats, nlons),dtype="float")
ice_land = np.zeros((nlats, nlons))
ice_post = np.zeros((nlats, nlons))

ice_land      = icefix.variables["land"]     [:,:]
ice_post      = icefix.variables["posteriori"][:,:]
ice_longitude = icefix.variables["longitude"][:,:]
ice_latitude  = icefix.variables["latitude"] [:,:]

ice_distance  = icefix.variables["distance_to_land"][:,:]
ice_distance /= 1000.   #Convert to km
#debug: print("read lon max ",ice_longitude.max(), flush=True )
