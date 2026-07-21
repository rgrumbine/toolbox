import os
from math import sin, cos, pi, ceil
import datetime

import numpy as np
import netCDF4 as nc

# Acquire basic data and average them
start = datetime.datetime(1980,1,1)
dt    = datetime.timedelta(1)
end   = datetime.datetime(2025,12,31)

# Do this to be able to start with a week that follows from 1980/1/1 but
#   doesn't require running through all earlier days -- some datagaps exist
tmp = datetime.datetime(2012,1,31)
tmp = datetime.datetime(1987,1,31)
tmp = datetime.datetime(1992,3,31)
tmp = datetime.datetime(1994,1,1)
nwk = (tmp-start)/dt/7
nwk = ceil(nwk)
#debug: print(nwk,  (tmp-start)/dt/7, flush=True)
start += nwk*dt*7
print('new start = ',start)
#debug: exit(0)


nx = 1536
ny =  768
nlayer = 15
ndays   = int((end-start)/dt + 1)
print('ndays = ',ndays)

Xdata = np.zeros((1, ny, nx, nlayer), dtype=np.float32)
Xavg  = np.zeros((ny, nx, nlayer), dtype=np.float32)
dtype = Xavg.dtype


tag   = start
week = 0
while(tag <= end-7*dt ):
  Xavg  = np.zeros((ny, nx, nlayer), dtype=np.float32)
  # rerun checking
  fname = "week."+tag.strftime("%Y%m%d")+".nc"
  if (os.path.exists(fname)):
      tag += 7*dt
      continue
  out = nc.Dataset(fname,"w")
  out.createDimension('ny',ny)
  out.createDimension('nx',nx)

  for count in range(0,7):

    flx = nc.Dataset('flx.'+tag.strftime("%Y%m%d")+'.nc')
    Xdata[0,:,:,0] = flx.variables['ICETK_surface'][0,:,:]
    Xdata[0,:,:,1] = flx.variables['ICEC_surface'][0,:,:]
    Xdata[0,:,:,2] = flx.variables['FDNSSTMP_surface'][0,:,:]
    Xdata[0,:,:,3] = flx.variables['USWRF_surface'][0,:,:]
    flx.close()

    prs = nc.Dataset('prs.'+tag.strftime("%Y%m%d")+'.nc')
    Xdata[0,:,:,4] = prs.variables['PRMSL_meansealevel'][0,:,:]
    Xdata[0,:,:,5] = prs.variables['HGT_1mb'][0,:,:]
    Xdata[0,:,:,6] = prs.variables['HGT_10mb'][0,:,:]
    Xdata[0,:,:,7] = prs.variables['HGT_200mb'][0,:,:]
    Xdata[0,:,:,8] = prs.variables['HGT_500mb'][0,:,:]
    Xdata[0,:,:,9] = prs.variables['HGT_700mb'][0,:,:]
    Xdata[0,:,:,10] = prs.variables['HGT_850mb'][0,:,:]
    prs.close()
  
    Xdata[0,:,:,11] = cos( (tag-start)/dt * 2.*pi/365.25)
    Xdata[0,:,:,12] = sin( (tag-start)/dt * 2.*pi/365.25)
    Xdata[0,:,:,13] = cos(2*(tag-start)/dt * 2.*pi/365.25)
    Xdata[0,:,:,14] = sin(2*(tag-start)/dt * 2.*pi/365.25)

    Xavg += Xdata[0]
    count += 1
    tag += dt

  Xavg /= 7

  out.createVariable('ICETK', dtype, ('ny', 'nx') )
  out.variables['ICETK'][:,:] = Xavg[:,:,0]

  out.createVariable('ICEC', dtype, ('ny', 'nx') )
  out.variables['ICEC'][:,:] = Xavg[:,:,1]

  out.createVariable('SST', dtype, ('ny', 'nx') )
  out.variables['SST'][:,:] = Xavg[:,:,2]

  out.createVariable('USWRF', dtype, ('ny', 'nx') )
  out.variables['USWRF'][:,:] = Xavg[:,:,3]

  out.createVariable('PRMSL', dtype, ('ny', 'nx') )
  out.variables['PRMSL'][:,:] = Xavg[:,:,4]

  out.createVariable('z1mb', dtype, ('ny', 'nx') )
  out.variables['z1mb'][:,:] = Xavg[:,:,5]

  out.createVariable('z10mb', dtype, ('ny', 'nx') )
  out.variables['z10mb'][:,:] = Xavg[:,:,6]

  out.createVariable('z200mb', dtype, ('ny', 'nx') )
  out.variables['z200mb'][:,:] = Xavg[:,:,7]

  out.createVariable('z500mb', dtype, ('ny', 'nx') )
  out.variables['z500mb'][:,:] = Xavg[:,:,8]

  out.createVariable('z700mb', dtype, ('ny', 'nx') )
  out.variables['z700mb'][:,:] = Xavg[:,:,9]

  out.createVariable('z850mb', dtype, ('ny', 'nx') )
  out.variables['z850mb'][:,:] = Xavg[:,:,10]

  # These could be ignored as their mean -> 0 and range is already +-1
  out.createVariable('cos', dtype, ('ny', 'nx') )
  out.variables['cos'][:,:] = Xavg[:,:,11]

  out.createVariable('sin', dtype, ('ny', 'nx') )
  out.variables['sin'][:,:] = Xavg[:,:,12]

  out.createVariable('cos2x', dtype, ('ny', 'nx') )
  out.variables['cos2x'][:,:] = Xavg[:,:,13]

  out.createVariable('sin2x', dtype, ('ny', 'nx') )
  out.variables['sin2x'][:,:] = Xavg[:,:,14]

  out.close()
  week += 1
