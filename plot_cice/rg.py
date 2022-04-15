#!/usr/bin/env python3
import argparse
import glob
import os

import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import netCDF4 as nc

import cartopy.crs as ccrs
import cartopy.feature as cfeature

print("hello")

def plot_world_map(lons, lats, data):
    # plot generic world map
    fig = plt.figure(figsize=(12,8))

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(central_longitude=30))
    ax.add_feature(cfeature.GSHHSFeature(scale='auto'))
    ax.set_extent([-180, 180, -90, 90])

    cmap='jet'
    cbarlabel = '%s' % ("hello1")
    plttitle = 'Plot of variable %s' % ("hello2")

    vmin = np.nanmin(data)
    vmax = np.nanmax(data)
    cs = ax.pcolormesh(lons, lats, data,vmin=vmin,vmax=vmax,cmap=cmap)
    cb = plt.colorbar(cs, extend='both', orientation='horizontal', shrink=0.5, pad=.04)
    cb.set_label(cbarlabel, fontsize=12)
    plt.title(plttitle)
    plt.savefig("hello.png")
    plt.close('all')

lons = range(0,360)
lats = range(-90,90)
data = np.zeros((len(lats),len(lons)))
print(len(lons), len(lats))

for i in range(0,360):
  data[:,i] = lats[:] 

plot_world_map(lons, lats, data)
