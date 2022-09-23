import os
import sys
import csv
import datetime
from datetime import date

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
    self.var = []
    self.name = str.strip(line[0])

    slat = line[1]
    slon = line[2]
    self.lat  = llparse(slat)
    self.lon  = llparse(slon)
    #retain the initial location for reference -- self.lat, self.lon will become .nc variables
    self.reflat = self.lat
    self.reflon = self.lon

    # RG: need to fix inv_locate so that it returns non-negative ints only, even
    #    after subtracting range
    tmp = z.inv_locate(self.lat, self.lon)
    self.i = int(0.5+tmp[0])
    self.j = int(0.5+tmp[1])
    if (self.i < 0 or self.j < 0):
      print("invlocate issue ",self.lat, self.lon, z.firstlat, z.firstlon, z.dlat, z.dlon, flush=True)
      exit(1)
    #debug print(self.name, "i,j = ",self.lat, self.lon, self.i, self.j, flush=True)
    self.lons = np.zeros((2*self.range_x+1))
    self.lats = np.zeros((2*self.range_y+1)) 
    ret = latpt()
    for i in range(-self.range_x, self.range_x+1):
      z.locate(i+self.i,self.j,ret)
      self.lons[i] = ret.lon
    for j in range(-self.range_y, self.range_y+1):
      z.locate(self.i, j+self.j, ret)
      self.lats[j] = ret.lat
    #debug print("new patch latlon range:",self.lats.max(), self.lats.min(), 
    #                     self.lons.max(), self.lons.min(), flush=True )


  def pncopen(self, fname, tag, cyc):
    self.ncfile = nc.Dataset(fname, mode='w', format='NETCDF4')
    self.lat_dim = self.ncfile.createDimension('lat', 2*self.range_x+1)
    self.lon_dim = self.ncfile.createDimension('lon', 2*self.range_y+1)
    self.time_dim = self.ncfile.createDimension('time', None)
    # Create variables to hold values for those referenced dimensions
    self.lat = self.ncfile.createVariable('lat', np.float32, ('lat',))
    self.lat.units = 'degrees_north'
    self.lat.long_name = 'latitude'
    self.lat[:] = self.lats[:]

    self.lon = self.ncfile.createVariable('lon', np.float32, ('lon',))
    self.lon.units = 'degrees_east'
    self.lon.long_name = 'longitude'
    self.lon[:] = self.lons[:]

    self.time = self.ncfile.createVariable('time', np.float64, ('time',))
    self.time.units = 'hours'

    self.yopp_header(fname)

  def yopp_header(self, fname):
    self.ncfile.title = fname
    self.ncfile.subtitle = "rg_subtitle"
    self.ncfile.setncattr("contributor_name","Robert Grumbine")
    self.ncfile.setncattr("contributor_email","Robert.Grumbine@noaa.gov")
    self.ncfile.setncattr("institution","NOAA/NWS/NCEP")
    self.ncfile.setncattr("source","NCEP GFS")
    self.ncfile.setncattr("creator_name","Robert Grumbine")
    self.ncfile.setncattr("creator_email","Robert.Grumbine@noaa.gov")
    tmp = date.today()
    #debug print("today = ",date.today(), tmp.strftime("%Y %m %d"), flush=True )
    self.ncfile.setncattr("date_created",tmp.strftime("%Y-%m-%d") )
    self.ncfile.setncattr("Conventions","conventions")
    self.ncfile.setncattr("standard_name_vocabulary","names")
    self.ncfile.setncattr("summary"," contribution to yopp sitemip")
    self.ncfile.setncattr("keywords","YOPP, Polar, Supersite")
    self.ncfile.setncattr("geospatial_lon_max","{:f}".format(self.lons.max() )  )
    self.ncfile.setncattr("geospatial_lon_min","{:f}".format(self.lons.min() )  )
    self.ncfile.setncattr("geospatial_lat_max","{:f}".format(self.lats.max() )  )
    self.ncfile.setncattr("geospatial_lat_min","{:f}".format(self.lats.min() )  )
    
    

# RG: need to manage name repeats.
  def addvar(self, grb):
    #debug print("addvar: ", grb.shortName,flush=True)
    try:
      tmp = self.ncfile.createVariable(grb.shortName, np.float32, ('time', 'lat','lon'), fill_value=9.e35)
    except:
      #debug print("could not create variable, name probably already in use ",grb.shortName,flush=True)
      return
    self.var.append(tmp)
    self.var[self.count].long_name = grb.name
    self.count += 1

  def extractvar(self, ftime, allvalues, vname):
    #Remember x,y are reversed from fortran
    #Vastly slower to use grb.values than to pass the decoded whole 
    #    grid and extract from it
    y = allvalues[ self.j-self.range_y : self.j+self.range_y+1, 
                   self.i-self.range_x : self.i+self.range_x+1 ]

    if (self.i*self.j != 0) :
      #debug print("extract shape: ",y.shape,self.i, self.j, self.range_x, 
      #   self.range_y, flush=True)
   
      #manage vname, time slicing:
      self.ncfile.variables[vname][ftime,:,:] = y
      self.time[ftime] = ftime

  def close(self):
    # close netcdf file associated w. patch
    #debug print("closing ",self.ncfile.title, flush=True )
    self.ncfile.close()
    #debug print("close",flush=True)

#---------------------------------------------------------------
