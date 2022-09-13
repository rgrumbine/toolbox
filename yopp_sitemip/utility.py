from grid import *

#---------------- Utilities -------------------------
# Parse a string to a value, later to add a
def llparse(x, standard="null"):
  # start with labelled string
  if (x[-1] == 'N' or x[-1] == 'E'):
    tmp = float(x[0:-1])
  elif (x[-1] == 'S' or x[-1] == 'W'):
    tmp = -float(x[0:-1])
  # else assume it's a clean number
  else:
    tmp = float(x)
#RG: Would be a good idea to have the option of enforcing some longitude standards
  return tmp

#Define standards by the minimum allowed longitude, -360, -180, 0
def lon_standards(x, lonmin = -999., lonmax = 999.):
  tmp = x
  if (tmp < lonmin):
    while(tmp < lonmin):
      tmp += 360.
  if (tmp > lonmax):
    while (tmp > lonmax):
      tmp -= 360.
  return tmp

#-------------
#extract lat-lon info from grbs[1]
def get_ll_info(y):
# y is the result of pygrib.open

# Assumes that all grids in file are regular lat-lon and same size and 
# shape as first field.
# Returns an llgrid with these specifications for any further manipulations needed
  lats, lons = y[1].latlons()
  dx = lons[:,1]-lons[:,2]
  dy = lats[1,:]-lats[2,:]
  firstlat = lats[0,0]
  firstlon = lons[0,0]
  delta_lat = dy[0]
  delta_lon = dx[0]
  nlon = lats.shape[1]
  nlat = lats.shape[0]
  print("dx max min: ",nlon, firstlon, delta_lon, dx.max(), dx.min(),dx.max() - dx.min() )
  print("dy max min: ",nlat, firstlat, delta_lat, dy.max(), dy.min(),dy.max() - dy.min() )
  z = llgrid(nx = nlon, ny = nlat, firstlon=firstlon, firstlat = firstlat, dlon = dx.max(), dlat = dy.max() )
  return z

