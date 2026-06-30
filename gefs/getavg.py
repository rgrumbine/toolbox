''' 
module getavg includes tools for getting average or climatological fields 
Robert Grumbine
30 June 2026
'''

import sys
import datetime
from math import pi, sin, cos

import numpy as np
import netCDF4 as nc

def getavg(Xavg, fname = 'thinned/average_1980.nc'):
  ''' getavg(Xavg, fname) -- get the long term average data '''
  try:
    avgs = nc.Dataset(fname, 'r')
  except:
    print("failed to open average file ",fname)
    sys.exit(1)

  Xavg[:,:,0] = avgs.variables['ICETK'][:,:]
  Xavg[:,:,1] = avgs.variables['ICEC'][:,:]
  Xavg[:,:,2] = avgs.variables['SST'][:,:]
  Xavg[:,:,3] = avgs.variables['USWRF'][:,:]
  Xavg[:,:,4] = avgs.variables['PRMSL'][:,:]
  Xavg[:,:,5] = avgs.variables['z1mb'][:,:]
  Xavg[:,:,6] = avgs.variables['z10mb'][:,:]
  Xavg[:,:,7] = avgs.variables['z200mb'][:,:]
  Xavg[:,:,8] = avgs.variables['z500mb'][:,:]
  Xavg[:,:,9] = avgs.variables['z700mb'][:,:]
  Xavg[:,:,10] = avgs.variables['z850mb'][:,:]
  Xavg[:,:,11] = 0.0
  Xavg[:,:,12] = 0.0
  Xavg[:,:,13] = 0.0
  Xavg[:,:,14] = 0.0
  Xavg[:,:,15] = 0.0
  Xavg[:,:,16] = 0.0

def getclimo(Xclimo, fbase):
  ''' getclimo(Xclimo, fbase) -- get the climatological fields '''
  k = 0
  for fname in 'ICETK', 'ICEC', 'SST', 'USWRF', 'PRMSL', 'z1mb', 'z10mb', 'z200mb', 'z500mb', \
          'z700mb', 'z850mb':
      #debug: print(k, fname, flush=True)
      try:
        data  = nc.Dataset(fname+'.nc','r')
      except:
        print("could not open climatology file ",fname+'.nc')
        sys.exit(1)
      # each variable has slope, intercept, sin, cos of 3 harmonics
      Xclimo[:,:,k,0] = data.variables['slope'][:,:]
      Xclimo[:,:,k,1] = data.variables['intercept'][:,:]
      Xclimo[:,:,k,2] = data.variables['cost'][:,:]
      Xclimo[:,:,k,3] = data.variables['sint'][:,:]
      Xclimo[:,:,k,4] = data.variables['cos2t'][:,:]
      Xclimo[:,:,k,5] = data.variables['sin2t'][:,:]
      Xclimo[:,:,k,6] = data.variables['cos3t'][:,:]
      Xclimo[:,:,k,7] = data.variables['sin3t'][:,:]
      data.close()
      k += 1

def makeclimo(Xclimo, ftag, epoch, Xout, nx, ny, nvar):
  dt      = datetime.timedelta(1)
  delta_d = (ftag - epoch)/dt
  Xout = np.zeros((ny,nx,nvar))
  for i in range(0, nvar):
    evaluate_epoch(Xclimo[:,:,i,:], delta_d, Xout[:,:,i])

def evaluate_epoch(Xclimo, delta_d, Xout):
  Xout  = Xclimo[1]
  Xout += Xclimo[0]*delta_d
  Xout += Xclimo[2]*cos(  delta_d*2.*pi/365.25)
  Xout += Xclimo[3]*sin(  delta_d*2.*pi/365.25)
  Xout += Xclimo[4]*cos(2*delta_d*2.*pi/365.25)
  Xout += Xclimo[5]*sin(2*delta_d*2.*pi/365.25)
  Xout += Xclimo[6]*cos(3*delta_d*2.*pi/365.25)
  Xout += Xclimo[7]*sin(3*delta_d*2.*pi/365.25)

