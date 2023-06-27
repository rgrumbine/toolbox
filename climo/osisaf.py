import os
import sys
import datetime

import numpy as np
import numpy.ma as ma
import netCDF4 as nc

start = datetime.datetime(2007,1,1)
current = start
end   = datetime.datetime(2021,12,31)
dt = datetime.timedelta(1)
obs = "1200.nc"
pole = "sh"

filecount = 0

while (current <= end):
  yy = current.strftime("%Y")
  mm = current.strftime("%m")
  dd = current.strftime("%d")
  fname = yy + "/" + mm +"/ice_conc_"+pole+"_polstere-100_multi_"+yy+mm+dd+obs 
  if (not os.path.exists(fname) ):
    print("missing ",fname)
    current += dt
    continue

  
  datanc = nc.Dataset(fname)
  filecount += 1
  if (current == start): 
    nx = len(datanc.dimensions['xc'])
    ny = len(datanc.dimensions['yc']) 
    lat = datanc.variables['lat'][:,:]
    lon = datanc.variables['lon'][:,:]
    print("nx ny lats lons ",nx, ny, lat.max(), lat.min(), lon.max(), lon.min(), flush=True )
    count = np.zeros((ny,nx))
    sum   = np.zeros((ny,nx))
    sumsq = np.zeros((ny,nx))

  # always available if file is:
  shortice_conc   = datanc.variables['ice_conc'][0,:,:]
  byte_confidence = datanc.variables['confidence_level'][0,:,:]
  byte_status     = datanc.variables['status_flag'][0,:,:]
  # not always available -- just since 2017/NN/NN
  shortice_conc_unfilter = datanc.variables['ice_conc_unfiltered'][0,:,:]
  byte_masks      = datanc.variables['masks'][0,:,:]

  if (shortice_conc.max() > 1000.): shortice_conc /= 100.
  if (shortice_conc.max() < 2.):    shortice_conc *= 100.
  print(current.strftime("%Y%m%d"),
        shortice_conc.max(), shortice_conc.min(),
        byte_confidence.max(), byte_confidence.min(),
        byte_status.max(), byte_confidence.min(),
        shortice_conc_unfilter.max(), shortice_conc_unfilter.min(),
        byte_masks.max(), byte_masks.min(),
        flush=True)

  #where(shortice_conc > 0 and shortice_conc <= 100): count += 1
  mask = ma.masked_array(shortice_conc > 0)
  mask = ma.logical_and(mask, shortice_conc <= 100)
  indices = mask.nonzero()
  for k in range(0,len(indices[0])):
    ti = indices[1][k]
    tj = indices[0][k]
    sum[tj,ti]   += shortice_conc[tj,ti]
    tmp  = shortice_conc[tj,ti]
    tmp *= shortice_conc[tj,ti]
    sumsq[tj,ti] += tmp
    count[tj,ti] += 1

  current += dt

print("filcount = ",filecount)
mask = ma.masked_array(count > 0)
indices = mask.nonzero()
for k in range(0,len(indices[0])):
  ti = indices[1][k]
  tj = indices[0][k]
  sum[tj,ti]   /= count[tj,ti]
  sumsq[tj,ti] /= count[tj,ti]

#rmse = np.zeros((ny,nx))
rmse = np.sqrt(sumsq)
print(sum.max(), sum.min(), sumsq.max(), sumsq.min(), rmse.max(), rmse.min() )
print((sumsq-sum*sum).max(), np.sqrt(sumsq-sum*sum).max()  )


