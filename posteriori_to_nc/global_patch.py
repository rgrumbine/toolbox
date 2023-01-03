import os
import sys
import datetime
from datetime import date

import numpy as np
  
import netCDF4 as nc

#RG library (also wants ijpt, latpt, const)
#mmablib/py in PYTHONPATH
from grid import *

#---------------------------------------------------------------
# Work on global grids

class global_patch:

#z is the llgrid definition
#z = llgrid(nx = nx, ny = ny, dlat = delta_lat, dlon = delta_lon, 
#               firstlon = firstlon, firstlat = firstlat)
  def  __init__(self, z, name):
    self.count   = 0   #count of variables
    self.name = name
    self.var = []
    self.nx  = z.nx
    self.ny  = z.ny
    self.lons = np.zeros((z.nx))
    self.lats = np.zeros((z.ny))
    ret = latpt()
    for i in range(0,self.nx):
      z.locate(i,0,ret)
      self.lons[i] = ret.lon
    for j in range(0, self.ny):
      z.locate(0, j, ret)
      self.lats[j] = ret.lat

  def header(self, fname):
    #Generic global header info:
    self.ncfile.title = fname
    self.ncfile.setncattr("institution","NOAA/NWS/NCEP")
    self.ncfile.setncattr("geospatial_lon_max","{:f}".format(self.lons.max() )  )
    self.ncfile.setncattr("geospatial_lon_min","{:f}".format(self.lons.min() )  )
    self.ncfile.setncattr("geospatial_lat_max","{:f}".format(self.lats.max() )  )
    self.ncfile.setncattr("geospatial_lat_min","{:f}".format(self.lats.min() )  )
    tmp = date.today()
    self.ncfile.setncattr("date_created",tmp.strftime("%Y-%m-%d") )

    #More specialized:
    self.ncfile.setncattr("contributor_name","Robert Grumbine")
    self.ncfile.setncattr("contributor_email","Robert.Grumbine@noaa.gov")
    self.ncfile.setncattr("creator_name","Robert Grumbine")
    self.ncfile.setncattr("creator_email","Robert.Grumbine@noaa.gov")
    #More specialized (kinds of things one might want):
    #self.ncfile.setncattr("source","NCEP GFS")
    #self.ncfile.setncattr("Conventions","conventions")
    #self.ncfile.setncattr("standard_name_vocabulary","names")
    #self.ncfile.setncattr("summary"," contribution to yopp sitemip")
    #self.ncfile.setncattr("keywords","YOPP, Polar, Supersite")


  def pncopen(self, fname):
    self.ncfile = nc.Dataset(fname, mode='w', format='NETCDF4')
    self.lat_dim = self.ncfile.createDimension('lat', self.ny)
    self.lon_dim = self.ncfile.createDimension('lon', self.nx)
    # Create variables to hold values for those referenced dimensions
    self.lat = self.ncfile.createVariable('lat', np.float32, ('lat',))
    self.lat.units = 'degrees_north'
    self.lat.long_name = 'latitude'
    self.lat[:] = self.lats[:]

    self.lon = self.ncfile.createVariable('lon', np.float32, ('lon',))
    self.lon.units = 'degrees_east'
    self.lon.long_name = 'longitude'
    self.lon[:] = self.lons[:]

    self.header(fname)


  def addvar(self, vname, dtype):
    #debug print('dtype = ',dtype, flush=True)
    if (dtype == 'uint8'):
      fill = 255
    else:
      print("failed type test")
      fill = 255

    try:
      tmp = self.ncfile.createVariable(vname, dtype, ( 'lat','lon'), fill_value=fill)
    except:
      return
    self.var.append(tmp)
    self.var[self.count].long_name = vname
    self.count += 1

  def encodevar(self, allvalues, vname):
    if (self.nx*self.ny != 0) :
      self.ncfile.variables[vname][:,:] = allvalues

  def close(self):
    # close netcdf file associated w. patch
    self.ncfile.close()

#---------------------------------------------------------------
