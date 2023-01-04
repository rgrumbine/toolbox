import numpy as np

from global_patch import *
from grid import *

nx   = int(360*12)
ny   = int(180*12)
dlat = -1./12.
dlon =  1./12.
#RG: Is this the correct flavor?
firstlat = +90 + dlat/2.
firstlon = dlon / 2.

z = llgrid(nx=nx, ny=ny, dlat=dlat, dlon=dlon, firstlon=firstlon, firstlat=firstlat)
#debug print(z, flush=True)

fin = open('seaice_posteriori_5min','rb')
dtype=np.dtype('ubyte')
x = np.zeros((ny,nx),dtype=dtype)
x = np.fromfile(fin, dtype=dtype, count=nx*ny)
x.shape = (ny,nx)
#debug print("max, min: ",x.max(), x.min(), flush=True )
#debug j = 0
#debug for i in range(0,nx,36):
#debug   print(i,j,x[j,i])
#debug j = ny - 1
#debug for i in range(0,nx,36):
#debug   print(i,j,x[j,i])
#debug exit(0)

#-------------------- Statistics of grid
updates = int(0)
count = np.zeros((256),dtype='int64')
area = np.zeros((256),dtype='float64')
allarea = 0.
for i in range(0,nx):
  for j in range(0,ny):
    if (x[j,i] == 2):
      updates += 1
      x[j,i] = 157
    if (x[j,i] == 224):
      updates += 1
      x[j,i] = 255

    count[int(x[j,i])] += 1
    #debug area[int(x[j,i])] += z.cellarea(j,i)
print("there were ",updates," updates to mask", flush=True)

#debug print("value count million km^2")
#debug for i in range(0,256):
#debug   if (count[i] != 0):
#debug     allarea += area[i]
#debug     print(i, count[i], area[i]/1.e6)
#debug print("\n",flush=True)
#debug print("all area: ",allarea/1.e6, flush=True)


# ---------------------   Netcdf -------------------------
fname = 'posteriori_5min.nc'
vname = 'posteriori_flag' 

gout = global_patch(z, fname)
gout.pncopen(fname)
gout.header('posteriori filter flags')
gout.ncfile.setncattr('source','https://polar.ncep.noaa.gov/mmab/papers/tn282/posteriori.pdf')
gout.addvar(vname, dtype)
gout.var[0].setncattr('flag 157','land')
gout.var[0].setncattr('flag 158','ocean > 26 C')
gout.var[0].setncattr('flag 159','ocean > 24 C')
gout.var[0].setncattr('flag 160','ocean > 22 C')
gout.var[0].setncattr('flag 161','ocean > 19 C')
gout.var[0].setncattr('flag 162','ocean > 15 C')
gout.var[0].setncattr('flag 163','ocean > 9 C')
gout.var[0].setncattr('flag 164','ocean > 2.15 C')
gout.var[0].setncattr('flag 165','ocean > -3 C')
gout.var[0].setncattr('flag 170','inland > 7 C')
gout.var[0].setncattr('flag 171','inland > 4 C')
gout.var[0].setncattr('flag 172','inland > 2.15 C')
gout.var[0].setncattr('flag 173','inland > 0 C')
gout.var[0].setncattr('flag 174','inland > -3 C')
gout.var[0].setncattr('flag 255','undefined')

gout.encodevar(x, vname)
gout.close()
 
