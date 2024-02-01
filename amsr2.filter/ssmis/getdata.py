import netCDF4
from netCDF4 import Dataset

#--------------------------------------------------------
# Use SST from qdoi v2, including its sea ice cover
sstgrid = Dataset('avhrr-only.nc', 'r', format='NETCDF4')
sst_nlats = len(sstgrid.dimensions["lat"])
sst_nlons = len(sstgrid.dimensions["lon"])

sst = np.zeros((sst_nlats, sst_nlons))
ice_sst = np.zeros((sst_nlats, sst_nlons))

sst   = sstgrid.variables["sst"][0,0,:,:]
ice_sst   = sstgrid.variables["ice"][0,0,:,:]

#--------------------------------------------------------
#read in skip (posteriori) file
#read in land mask file
#read in distance to land

icefix = Dataset('seaice_fixed_fields.nc', 'r', format='NETCDF4')
nlats = len(icefix.dimensions["nlats"])
nlons = len(icefix.dimensions["nlons"])

ice_longitude = np.zeros((nlats, nlons),dtype="double")
ice_latitude = np.zeros((nlats, nlons),dtype="double")
ice_distance = np.zeros((nlats, nlons),dtype="float")

ice_land = np.zeros((nlats, nlons))
ice_land = icefix.variables["land"]     [:,:]

ice_post = np.zeros((nlats, nlons))
ice_post = icefix.variables["posteriori"][:,:]
print("ice post max min ",ice_post.max(), ice_post.min() )

ice_longitude = icefix.variables["longitude"][:,:]
ice_latitude  = icefix.variables["latitude"] [:,:]
ice_distance  = icefix.variables["distance_to_land"][:,:]
ice_distance /= 1000.   #Convert to km

###############################################################

tb = np.zeros((7))

icenc = Dataset('l2out.f248.51.nc', 'r', format='NETCDF4')
nobs = len(icenc.dimensions["nobs"])
print("nobs = ",nobs, flush=True)
longitude = np.zeros((nobs))
latitude = np.zeros((nobs))
icec = np.zeros((nobs))
quality = np.zeros((nobs), dtype='int')
satid = np.zeros((nobs), dtype='int')
land = np.zeros((nobs))
dtg1 = np.zeros((nobs), dtype='int')
dtg2 = np.zeros((nobs), dtype='int')
t19v = np.zeros((nobs))
t19h = np.zeros((nobs))
t22v = np.zeros((nobs))
t37v = np.zeros((nobs))
t37h = np.zeros((nobs))
t85v = np.zeros((nobs))
t85h = np.zeros((nobs))

longitude = icenc.variables["longitude"][:]
latitude = icenc.variables["latitude"][:]
icec = icenc.variables["ice_concentration"][:]
quality = icenc.variables["quality"][:]
satid = icenc.variables["satid"][:]
land = icenc.variables["land_flag"][:]
dtg1 = icenc.variables["dtg_yyyymmdd"][:]
dtg2 = icenc.variables["dtg_hhmm"][:]
t19v = icenc.variables["tb_19V"][:]
t19h = icenc.variables["tb_19H"][:]
t22v = icenc.variables["tb_22V"][:]
t37v = icenc.variables["tb_37V"][:]
t37h = icenc.variables["tb_37H"][:]
t85v = icenc.variables["tb_85V"][:]
t85h = icenc.variables["tb_85H"][:]

###############################################################
