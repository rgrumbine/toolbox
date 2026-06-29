from math import sin, cos, pi
import datetime

import numpy as np
import netCDF4 as nc

# Acquire basic data and average them
start = datetime.datetime(1980,1,1)
dt    = datetime.timedelta(1)
end   = datetime.datetime(1985,12,31)

nx = 1536
ny =  768
nlayer = 15
ndays   = int((end-start)/dt + 1)
print('ndays = ',ndays)

Xdata = np.zeros((1, ny, nx, nlayer), dtype=np.float32)
Xavg  = np.zeros((ny, nx, nlayer), dtype=np.float32)

tag   = start
count = 0
while(tag <= end and count < ndays):
  print(count, "tag = ",tag, flush = True)

  flx = nc.Dataset('flx.'+tag.strftime("%Y%m%d")+'.nc')
  Xdata[count,:,:,0] = flx.variables['ICETK_surface'][0,:,:]
  Xdata[count,:,:,1] = flx.variables['ICEC_surface'][0,:,:]
  Xdata[count,:,:,2] = flx.variables['FDNSSTMP_surface'][0,:,:]
  Xdata[count,:,:,3] = flx.variables['USWRF_surface'][0,:,:]
  flx.close()

  prs = nc.Dataset('prs.'+tag.strftime("%Y%m%d")+'.nc')
  Xdata[count,:,:,4] = prs.variables['PRMSL_meansealevel'][0,:,:]
  Xdata[count,:,:,5] = prs.variables['HGT_1mb'][0,:,:]
  Xdata[count,:,:,6] = prs.variables['HGT_10mb'][0,:,:]
  Xdata[count,:,:,7] = prs.variables['HGT_200mb'][0,:,:]
  Xdata[count,:,:,8] = prs.variables['HGT_500mb'][0,:,:]
  Xdata[count,:,:,9] = prs.variables['HGT_700mb'][0,:,:]
  Xdata[count,:,:,10] = prs.variables['HGT_850mb'][0,:,:]
  prs.close()

  Xdata[count,:,:,11] = cos( (tag-start)/dt * 2.*pi/365.25)
  Xdata[count,:,:,12] = sin( (tag-start)/dt * 2.*pi/365.25)
  Xdata[count,:,:,13] = cos(2*(tag-start)/dt * 2.*pi/365.25)
  Xdata[count,:,:,14] = sin(2*(tag-start)/dt * 2.*pi/365.25)

  Xavg += Xdata[count]

  #count += 1
  tag += dt

Xavg /= ndays

# Print out max, min of each layer's average
for l in range(0,nlayer):
    print(l, Xavg[:,:,l].max(), Xavg[:,:,l].min(), flush=True )

# RG: Save average fields and scaling factor so as to be able to run on new data

out = nc.Dataset("out.nc","w")
out.createDimension('ny',ny)
out.createDimension('nx',nx)

dtype = Xavg.dtype
print("dtype = ",dtype)

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
