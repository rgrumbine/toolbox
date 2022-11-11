#!/usr/bin/env python3
import argparse
import glob
import os

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import netCDF4 as nc

import cartopy.crs as ccrs
import cartopy.feature as cfeature

matplotlib.use('agg')

def plot_world_map(lons, lats, data):
    vmin = np.nanmin(data)
    vmax = np.nanmax(data)

    ax = plt.axes(projection=ccrs.LambertCylindrical() )
    fig = plt.figure(figsize=(12,8))

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.LambertCylindrical() )

    ax.set_extent([-100,-60, 30, 70], crs=ccrs.LambertCylindrical())

    #ax.add_feature(cfeature.GSHHSFeature(levels=[1],scale="l" ) )
    #ax.add_feature(cfeature.GSHHSFeature(levels=[2],scale="l" ) )
    #ax.add_feature(cfeature.GSHHSFeature(levels=[3],scale="l" ) )
    #ax.add_feature(cfeature.GSHHSFeature(levels=[4],scale="l" ) )
    #ax.add_feature(cfeature.GSHHSFeature(scale="l" ) )
    #ax.add_feature(cfeature.GSHHSFeature( ) )
    ax.add_feature(cfeature.GSHHSFeature(levels=[1,2], scale="f") )
    plt.savefig("hello1.png")
    #exit(0)

    colors='jet'
    cbarlabel = '%s' % ("hello1")
    plttitle = 'Plot of variable %s' % ("hello2")
    plt.title(plttitle)

    plt.savefig("hello2.png")

    cs = ax.pcolormesh(lons, lats, data,vmin=vmin,vmax=vmax,cmap=colors)
    cb = plt.colorbar(cs, extend='both', orientation='horizontal', shrink=0.5, pad=.04)
    cb.set_label(cbarlabel, fontsize=12)

    plt.savefig("hello3.png")

    plt.close('all')

#----------------------------------------------------------------
lons = range(-180,360)
lats = range(-90,90)
data = np.zeros((len(lats),len(lons)))

for i in range(-180,360):
  data[:,i] = lats[:] 

plot_world_map(lons, lats, data)
print("back in main",flush=True)

#ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(central_longitude=30))
#ax.set_extent([-180, 180, -90, 90])
