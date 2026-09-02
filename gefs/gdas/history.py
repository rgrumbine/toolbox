import sys
import os
from math import sin, cos, pi, ceil
import datetime

import numpy as np
import netCDF4 as nc

# Acquire basic data and average them
end   = datetime.datetime.today()
dt    = datetime.timedelta(1)
start = datetime.datetime(1980,1,1)
tmp = datetime.datetime(2026,6,16)
nwk = (tmp - start)/dt/7
nwk = ceil(nwk)
start += nwk*dt*7
#debug: print("start = ",start, flush=True)
#debug: sys.exit(0)


nx = 1536
ny =  768
nlayer  = 21

Xdata = np.zeros((1, ny, nx, nlayer), dtype=np.float32)
dtype = Xdata.dtype

tag   = start
while(tag <= end - 7*dt ):
  Xavg  = np.zeros((ny, nx, nlayer), dtype=np.float32)

  fname = "week2."+tag.strftime("%Y%m%d")+".nc"

  out = nc.Dataset(fname,"w")
  out.createDimension('ny',ny)
  out.createDimension('nx',nx)

  for count in range(0,7):

    prs = nc.Dataset('prs.'+tag.strftime("%Y%m%d")+'.nc')
    Xdata[0,:,:,14] = prs.variables['PRMSL_meansealevel'][0,:,:]
    Xdata[0,:,:,15] = prs.variables['HGT_1mb'][0,:,:]
    Xdata[0,:,:,16] = prs.variables['HGT_10mb'][0,:,:]
    Xdata[0,:,:,17] = prs.variables['HGT_200mb'][0,:,:]
    Xdata[0,:,:,18] = prs.variables['HGT_500mb'][0,:,:]
    Xdata[0,:,:,19] = prs.variables['HGT_700mb'][0,:,:]
    Xdata[0,:,:,20] = prs.variables['HGT_850mb'][0,:,:]
    prs.close()
  
    flx = nc.Dataset('flx.'+tag.strftime("%Y%m%d")+'.nc')
    Xdata[0,:,:,0] = flx.variables['ICETK_surface'][0,:,:]
    Xdata[0,:,:,1] = flx.variables['ICEC_surface'][0,:,:]
    Xdata[0,:,:,2] = flx.variables['FDNSSTMP_surface'][0,:,:]
    Xdata[0,:,:,3] = flx.variables['USWRF_surface'][0,:,:]
    Xdata[0,:,:,4] = flx.variables['TMP_surface'][0,:,:]
    Xdata[0,:,:,6] = flx.variables['TMP_2maboveground'][0,:,:]
    Xdata[0,:,:,7] = flx.variables['SPFH_2maboveground'][0,:,:]
    Xdata[0,:,:,8] = flx.variables['UGRD_10maboveground'][0,:,:]
    Xdata[0,:,:,9] = flx.variables['VGRD_10maboveground'][0,:,:]
    Xdata[0,:,:,10] = flx.variables['SHTFL_surface'][0,:,:]
    Xdata[0,:,:,11] = flx.variables['LHTFL_surface'][0,:,:]
    Xdata[0,:,:,12] = flx.variables['PWAT_entireatmosphere_consideredasasinglelayer_'][0,:,:]
    Xdata[0,:,:,13] = flx.variables['LAND_surface'][0,:,:]

    #Xdata[0,:,:,5] = flx.variables['LANDFRC_surface'][0,:,:]
    flx.close()

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

  out.createVariable('TMPs', dtype, ('ny', 'nx') )
  out.variables['TMPs'][:,:] = Xavg[:,:,4]

  #out.createVariable('LANDFRC', dtype, ('ny', 'nx') )
  #out.variables['LANDFRC'][:,:] = Xavg[:,:,5]

  out.createVariable('TMP2m', dtype, ('ny', 'nx') )
  out.variables['TMP2m'][:,:] = Xavg[:,:,6]

  out.createVariable('SPFH2m', dtype, ('ny', 'nx') )
  out.variables['SPFH2m'][:,:] = Xavg[:,:,7]

  out.createVariable('U10m', dtype, ('ny', 'nx') )
  out.variables['U10m'][:,:] = Xavg[:,:,8]

  out.createVariable('V10m', dtype, ('ny', 'nx') )
  out.variables['V10m'][:,:] = Xavg[:,:,9]

  out.createVariable('SHTFL', dtype, ('ny', 'nx') )
  out.variables['SHTFL'][:,:] = Xavg[:,:,10]

  out.createVariable('LHTFL', dtype, ('ny', 'nx') )
  out.variables['LHTFL'][:,:] = Xavg[:,:,11]

  out.createVariable('PWAT', dtype, ('ny', 'nx') )
  out.variables['PWAT'][:,:] = Xavg[:,:,12]

  out.createVariable('LAND', dtype, ('ny', 'nx') )
  out.variables['LAND'][:,:] = Xavg[:,:,13]

  out.createVariable('PRMSL', dtype, ('ny', 'nx') )
  out.variables['PRMSL'][:,:] = Xavg[:,:,14]

  out.createVariable('z1mb', dtype, ('ny', 'nx') )
  out.variables['z1mb'][:,:] = Xavg[:,:,15]

  out.createVariable('z10mb', dtype, ('ny', 'nx') )
  out.variables['z10mb'][:,:] = Xavg[:,:,16]

  out.createVariable('z200mb', dtype, ('ny', 'nx') )
  out.variables['z200mb'][:,:] = Xavg[:,:,17]

  out.createVariable('z500mb', dtype, ('ny', 'nx') )
  out.variables['z500mb'][:,:] = Xavg[:,:,18]

  out.createVariable('z700mb', dtype, ('ny', 'nx') )
  out.variables['z700mb'][:,:] = Xavg[:,:,19]

  out.createVariable('z850mb', dtype, ('ny', 'nx') )
  out.variables['z850mb'][:,:] = Xavg[:,:,20]


  out.close()
