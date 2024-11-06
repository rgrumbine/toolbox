import os
import sys
import numpy as np
import numpy.ma as ma

#----------------------------------------------
def oiv2(lat, lon):
  dlat = 0.25
  dlon = 0.25
  firstlat = -89.875
  firstlon = 0.125
  if (lon < 0):
    lon += 360.
  j = int(round( (lat - firstlat)/dlat ))
  i = int(round( (lon - firstlon)/dlon ))
  return (j,i)

def rg12th(lat, lon):
  dlat = -1./12.
  dlon =  1./12.
  firstlat = 90. - dlat/2.
  firstlon = dlon/2.
  if (lon < 0):
    lon += 360.
  j = int(round( (lat - firstlat)/dlat ))
  i = int(round( (lon - firstlon)/dlon ))
  return (j,i)

def delta(x,y):
  return (x-y)/(x+y)

#----------------------------------------------
# satellite processes
# delta ratio
def delta(x,y):
  return (x-y)/(x+y)

#A stokes parameter
def delta2(x,y):
  d = x*x
  s = x*x
  d -= y*y
  s += y*y
  #debug: print("d, s, d/s",d.max(), d.min(), s.max(), s.min(), (d/s).max(), (d/s).min(), flush=True )
  return (d/s)
  #return (x*x-y*y)/(x*x+y*y)

#----------------------------------------------
# More tools

def near(x, y, delta):
    return(fabs(x-y) < delta)

#----------------------------------------------
def imsice(ims):
  if (ims[0] == 3 and
      ims[1] == 3 and
      ims[2] == 3 and
      ims[3] == 3 and
      ims[4] == 3):
    return True
  else:
    return False

def imsopen(ims):
  if (ims[0] == 1 and
      ims[1] == 1 and
      ims[2] == 1 and
      ims[3] == 1 and
      ims[4] == 1):
    return True
  else:
    return False
#----------------------------------------------------------


