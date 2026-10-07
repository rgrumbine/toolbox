'''
# collection bin for miscellaneous functions
'''
import copy
import datetime
from math import floor, ceil

import numpy as np
import netCDF4 as nc

import cartopy.crs as ccrs
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')

#=================================================================
def show(bins, lons, lats, x, title, fbase, cmap = matplotlib.colormaps.get_cmap('bwr'), \
         proj = ccrs.PlateCarree() ):
  ''' show(bins, lons, lats, x, title, fbase, cmap = , proj = '''
  bounds = np.array(bins)
  norm = matplotlib.colors.BoundaryNorm(boundaries = bounds, ncolors = 256)

  fig = plt.figure(figsize=(12, 9))
  ax  = fig.add_subplot(1, 1, 1, projection = proj)

  #WNA: ax.set_extent((-95, -15, 0, 75),crs=proj)
  #Nino 3.4: ax.set_extent((-170, -120, -5, 5), crs=proj)

  ax.coastlines(resolution='10m')
  ax.gridlines()

  cs = ax.pcolormesh(lons, lats, x, norm = norm, cmap = cmap, transform=ccrs.PlateCarree() )
  cb = plt.colorbar(cs, extend='both', orientation='horizontal', shrink=0.5, pad=.04)
  cbarlabel = str(title)
  cb.set_label(cbarlabel, fontsize=12)

  plt.savefig(fbase+".png")
  plt.close()

  hist, binedges =  np.histogram(x, bins = bins)
  print(title)
  print(hist, hist.sum() )
  print(binedges,"\n\n")
  #debug: print(binedges, flush=True)

#=================================================================
def applymask(grid, indices):
  ''' applymask(grid, indices) -- indices being array indices from masked array '''
  for k in range(0, len(indices[0])):
    i = indices[1][k]
    j = indices[0][k]
    grid[j,i] = 0.

#=================================================================
def find_bins(x, nbin):
  ''' find_bins(x, nbin) returns an np.linspace(vmin, vmax, nbin) '''
  vmin = floor(np.nanmin(x))
  vmax = ceil(np.nanmax(x))
  #debug: print("find bins max min ",vmax, vmin, nbin, flush=True)
  return np.linspace(vmin, vmax, nbin)

#=================================================================
def climo(intercept, slope, ampl, phase, freq, epoch, tag):
  ''' climo(intercept, slope, ampl, phase, freq, epoch, tag) 
      intercept, slope = linear trend
      ampl, phase = amplitude and phase of the harmonics
      freq        = frequency of the harmonics
      epoch = reference date of the climatology
      tag   = date climatology is desired for
  '''
  delta = (tag - epoch).days
  sst = copy.deepcopy(intercept)
  sst += slope*delta
  for j in range(0,3):
    sst += ampl[j]*np.cos(phase[j] + freq[j]*delta)

  return sst
