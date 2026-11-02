'''
plot maps of new climatology's statistics
Robert Grumbine
30 October 2026
'''
import sys
import datetime
import copy

import numpy as np
from numpy import ma

import netCDF4 as nc
import cartopy.crs as ccrs
import matplotlib
import matplotlib.pyplot as plt

from functions import show, find_bins

matplotlib.use('Agg')

import epoch

#=================================================================

# given the mean values of sumx1, sumx2, sumx3, sumx4, compute
#    mean, sd, skew, kurtosis

nx = 1536
ny =  768
#epoch = epoch.epoch
#print("epoch = ",epoch)

climate = epoch.epoch(sys.argv[1])

tag_jan1 = datetime.datetime(2007,1,1)
tag_jan2 = datetime.datetime(2025,1,1)
tag_jul1 = datetime.datetime(2007,7,1)

jan1 = climate.climo(tag_jan1)
jan2 = climate.climo(tag_jan2)
jul1 = climate.climo(tag_jul1)

print("jan1 max min ",jan1.max(), jan1.min() )
print("jan2 max min ",jan2.max(), jan2.min() )
print("jul1 max min ",jul1.max(), jul1.min() )
#----------------------------------------------------------------------
proj  = ccrs.PlateCarree()

#----------------------------------------------------------------------
#Jan 1

if (jan1.max() > 273):
    jan1 -= 273.15

if (jan2.max() > 273):
    jan2 -= 273.15

bins = np.linspace(-3, 40, 44)

colors = matplotlib.colormaps.get_cmap('bwr')

# For nonuniform binning:
bounds = np.array(bins)
norm = matplotlib.colors.BoundaryNorm(boundaries = bounds, ncolors = 256)

fig = plt.figure(figsize=(12, 9))
ax  = fig.add_subplot(1, 1, 1, projection = proj)
ax.coastlines(resolution='10m')
ax.gridlines()

cs = ax.pcolormesh(climate.lons, climate.lats, jan1, norm = norm, cmap = colors, transform=ccrs.PlateCarree() )
cb = plt.colorbar(cs, extend='both', orientation='horizontal', shrink=0.5, pad=.04)
cbarlabel = '%s' % ("jan1")
cb.set_label(cbarlabel, fontsize=12)

plt.savefig("jan1.png")
plt.close()

hist, binedges =  np.histogram(jan1, bins = bins)
print("jan1 histogram ",hist)
print(binedges)

#----------------------------------------------------------------------
#Jul 1
if (jul1.max() > 273):
    jul1 -= 273.15

fig = plt.figure(figsize=(12, 9))
ax  = fig.add_subplot(1, 1, 1, projection = proj)
ax.coastlines(resolution='10m')
ax.gridlines()

cs = ax.pcolormesh(climate.lons, climate.lats, jul1, norm = norm, cmap = colors, transform=ccrs.PlateCarree() )
cb = plt.colorbar(cs, extend='both', orientation='horizontal', shrink=0.5, pad=.04)
cbarlabel = '%s' % ("jul1")
cb.set_label(cbarlabel, fontsize=12)

plt.savefig("jul1.png")
plt.close()

hist, binedges =  np.histogram(jul1, bins = bins)
print(hist, hist.sum() )
print(binedges)

#----------------------------------------------------------------------
#Jan 1 2025
fig = plt.figure(figsize=(12, 9))
ax  = fig.add_subplot(1, 1, 1, projection = proj)
ax.coastlines(resolution='10m')
ax.gridlines()

cs = ax.pcolormesh(climate.lons, climate.lats, jan2, norm = norm, cmap = colors, transform=ccrs.PlateCarree() )
cb = plt.colorbar(cs, extend='both', orientation='horizontal', shrink=0.5, pad=.04)
cbarlabel = '%s' % ("jan1 2025")
cb.set_label(cbarlabel, fontsize=12)

plt.savefig("jan2025.png")
plt.close()

hist, binedges =  np.histogram(jan2, bins = bins)
print(hist, hist.sum() )
print(binedges)

#sys.exit(0)
#----------------------------------------------------------------------
#delta:
delta = copy.deepcopy(jul1)
delta -= jan1
print("delta ",delta.max(), delta.min() )

#RG: binning of annual cycle amplitudes
#bins = [0, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1., 1.5, 2, 3, 3.5, 5 ]
bins = np.linspace(-20,20,41)

colors = matplotlib.colormaps.get_cmap('bwr')

# For nonuniform binning:
bounds = np.array(bins)
norm = matplotlib.colors.BoundaryNorm(boundaries = bounds, ncolors = 256)

fig = plt.figure(figsize=(12, 9))
ax  = fig.add_subplot(1, 1, 1, projection = proj)
ax.coastlines(resolution='10m')
ax.gridlines()

cs = ax.pcolormesh(climate.lons, climate.lats, delta, norm = norm, cmap = colors, transform=ccrs.PlateCarree() )
cb = plt.colorbar(cs, extend='both', orientation='horizontal', shrink=0.5, pad=.04)
cbarlabel = '%s' % ("Jul1 - Jan1")
cb.set_label(cbarlabel, fontsize=12)

plt.savefig("delta.png")
plt.close()

hist, binedges =  np.histogram(delta, bins = bins)
print(hist, hist.sum() )
print(binedges)
#----------------------------------------------------------------------
#delta:
delta = copy.deepcopy(jan2)
delta -= jan1
print("delta 2025 - 2007",delta.max(), delta.min() )

#RG: binning of annual cycle amplitudes
bins = np.linspace(-15,15,31)
bins = [-15, -5, -2.5, -1, -0.5, 0, 0.5, 1, 2.5, 5, 15]

colors = matplotlib.colormaps.get_cmap('bwr')

# For nonuniform binning:
bounds = np.array(bins)
norm = matplotlib.colors.BoundaryNorm(boundaries = bounds, ncolors = 256)

fig = plt.figure(figsize=(12, 9))
ax  = fig.add_subplot(1, 1, 1, projection = proj)
ax.coastlines(resolution='10m')
ax.gridlines()

cs = ax.pcolormesh(climate.lons, climate.lats, delta, norm = norm, cmap = colors, transform=ccrs.PlateCarree() )
cb = plt.colorbar(cs, extend='both', orientation='horizontal', shrink=0.5, pad=.04)
cbarlabel = '%s' % ("Jan2 - Jan1")
cb.set_label(cbarlabel, fontsize=12)

plt.savefig("delta2.png")
plt.close()

hist, binedges =  np.histogram(delta, bins = bins)
print(hist, hist.sum() )
print(binedges)
