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
    self.range_x = int(abs(1./z.dlon)+1.5)
    self.range_y = int(abs(1./z.dlat)+1.5)
    print("ranges = ",self.range_x, self.range_y)

    self.name = str.strip(line[0])
    self.slat = line[1]
    self.slon = line[2]
    self.lat  = llparse(self.slat)
    self.lon  = llparse(self.slon)
    # want range to be 1 degree -- note should attend signs, boundaries RG
    self.flat = max(-90.,self.lat - 1.0)
    self.flon = self.lon-1.
    tmp = z.inv_locate(self.flat, self.flon)
    self.i = tmp[0]
    self.j = tmp[1]
    print("i,j = ",self.i, self.j, tmp[0], tmp[1])


  def pncopen(self, fname, tag, cyc):
    # Establish netcdf4 file for writing, using fname
    # write out:
    #    name, nx, ny, lat, lon as file variables
    #    date and cycle of forecast too
    self.ncfile = nc.Dataset(fname, mode='w', format='NETCDF4')
    print("pncopen",self.ncfile)

  def addvar(self, name, level, typeOfLevel):
    # nc add variable
    print("addvar")

  def extractvar(self, grb):
    # check for name repeats?
    y = grb.values[self.i-self.range_x: self.i+self.range_x, self.j-self.range_y:self.j+self.range_y]
    #grb.fcst_hr

  def close(self):
    # close netcdf file associated w. patch
    self.ncfile.close()

    print("close")

#---------------------------------------------------------------
