import os
import sys
import csv
import datetime

import numpy as np
  
import pygrib
import netCDF4 as nc

#RG library (also wants ijpt, latpt, const)
#mmablib/py in PYTHONPATH
from grid import *

#Local utilities:
from utility import *

#---------------------------------------------------------------
# Work with the YOPP Site locations

class patches:

#z is the llgrid definition
#line is the line read in from loc4.csv
#z = llgrid(nx = nx, ny = ny, dlat = delta_lat, dlon = delta_lon, 
#               firstlon = firstlon, firstlat = firstlat)
  def  __init__(self, z, line):
    self.count   = 0   #count of variables
    self.range_x = int(abs(1./z.dlon)+1.5)
    self.range_y = int(abs(1./z.dlat)+1.5)
    #debug print("ranges = ",self.range_x, self.range_y, flush=True)

    self.name = str.strip(line[0])
    self.slat = line[1]
    self.slon = line[2]
    self.lat  = llparse(self.slat)
    self.lon  = llparse(self.slon)
    # want range to be 1 degree -- note should attend signs, boundaries RG
    self.flat = max(-90.,self.lat - 1.0)
    self.flon = self.lon-1.
    # RG: need to fix inv_locate so that it returns non-negative ints only, even
    #    after subtracting range
    tmp = z.inv_locate(self.flat, self.flon)
    self.i = int(0.5+tmp[0])
    self.j = int(0.5+tmp[1])
    print(self.name, "i,j = ",self.flat, self.flon, self.i, self.j, flush=True)
    self.var = []


  def pncopen(self, fname, tag, cyc):
    # Establish netcdf4 file for writing, using fname
    # write out:
    #    name, nx, ny, lat, lon as file variables
    #    date and cycle of forecast too
    self.ncfile = nc.Dataset(fname, mode='w', format='NETCDF4')
    self.ncfile.title = "YOPP Sitemip Patch "+self.name
    self.ncfile.subtitle = "for cycle "+cyc + " on "+tag
    self.lat_dim = self.ncfile.createDimension('lat', 2*self.range_x+1)
    self.lon_dim = self.ncfile.createDimension('lon', 2*self.range_y+1)
    self.time_dim = self.ncfile.createDimension('time', None)
    #debug print(self.ncfile.title, self.lat_dim, self.lon_dim, self.time_dim, flush=True)
    #debug print("pncopen",self.ncfile,flush=True)

  def addvar(self, grb):
    # nc add variable
    if (self.count == 0):
      print("count = ",self.count, flush=True)
      self.lat = self.ncfile.createVariable('lat', np.float32, ('lat',))
      self.lat.units = 'degrees_north'
      self.lat.long_name = 'latitude'
      self.lon = self.ncfile.createVariable('lon', np.float32, ('lon',))
      self.lon.units = 'degrees_east'
      self.lon.long_name = 'longitude'
      self.time = self.ncfile.createVariable('time', np.float64, ('time',))
    #debug print("addvar: ", grb.shortName,flush=True)
    try:
      tmp = self.ncfile.createVariable(grb.shortName, np.float32, ('lat','lon'), fill_value=9.e35)
    except:
      #debug print("could not create variable, name probably already in use ",grb.shortName,flush=True)
      return
    self.var.append(tmp)
    self.var[self.count].long_name = grb.name
    self.count += 1

  def extractvar(self, grb):
    # check for name repeats?
    y = grb.values[self.i-self.range_x: self.i+self.range_x, self.j-self.range_y:self.j+self.range_y]
    print("extract shape: ",y.shape)
    #grb.fcst_hr

  def close(self):
    # close netcdf file associated w. patch
    print("closing ",self.ncfile.title )
    self.ncfile.close()
    #debug print("close",flush=True)

#---------------------------------------------------------------
