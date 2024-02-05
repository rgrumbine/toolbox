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


