import sys
import netCDF4 as nc

def getavg(Xavg, fname = 'thinned/average_1980.nc'):
  try:
    avgs = nc.Dataset(fname, 'r')
  except:
    print("failed to open file ",fname)
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


