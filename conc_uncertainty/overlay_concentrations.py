

"""
Given N > 1 concentration grids, find average and variance. Then 
HSV output of reslt, with H = H(average), S = S(variance) s.t.
high saturation = low variance. V = fixed/reserved for a player to be
named later


"""

import sys
import os
import datetime

from math import *
import numpy as np
import numpy.ma as ma

import netCDF4 as nc
import pygrib

import matplotlib
import matplotlib.pyplot as plt
#from matplotlib  import colormaps
#from matplotlib  import colors

#---------------------------------------------------
# Read in some concentrations, find mean and sqrt(variance)
base='/ncrc/home1/Robert.Grumbine/scratch/Verification_data/ice5min.new/'
fn="ice5min.201903"

fname = base + fn
grbs = pygrib.open(fname)
grbindex = pygrib.index(fname)
#debug: print(grbindex, flush=True)
#debug: print(grbindex.keys, flush=True)

lats, lons = grbs[1].latlons()
nlon = lats.shape[1]
nlat = lats.shape[0]
print("nx, ny ",nlon, nlat)

sumx = np.zeros((nlat, nlon))
sumx2 = np.zeros((nlat, nlon))
ndays=30
for i in range(1,ndays+1):
  print(i, grbs[i].values.max() )
  sumx += grbs[i].values
  sumx2 += grbs[i].values*grbs[i].values

sumx /= ndays
sumx2 /= ndays
print("sumx ",sumx.max(), sumx.min(), "sumx2 ",sumx2.max(), sumx2.min() )

var = sumx2 - sumx*sumx
var = np.max(var, 0)
print("var ",var.max(), var.min() )
sd = np.sqrt(var)
print("sd ",sd.max(), sd.min() )





#---------------------------------------------------
#create a colormap
#  then assign bounds
#  then run norm to normalize vs. values of the bounds
#  finally, plot figure and color bar

colors = [
  "#0000ff",
  "#0000bb",
  "#000088",
  "#000044" ]
my_cmap = matplotlib.colors.ListedColormap(colors, name="my_cmap")
bounds = [1./255., 0.15, 0.40, 0.80, 1.0]
norm = matplotlib.colors.BoundaryNorm(bounds, my_cmap.N)

# Demo of the basic color bar:
fig,ax = plt.subplots(figsize=(8,6))

#fig.colorbar(
#    matplotlib.cm.ScalarMappable(cmap=my_cmap, norm=norm),
#    cax=ax, orientation='horizontal',
#    extend='both',
#    spacing='proportional'
#  )

plt.pcolormesh(sumx, cmap = my_cmap)
fig.savefig("sumx.png")
plt.close()

#fig,ax = plt.subplots(figsize=(8,6))
#plt.pcolormesh(sumx2, cmap = my_cmap)
#fig.savefig("sumx2.png")
#plt.close()


#colorsys.rgb_to_hsv(r, g, b)
