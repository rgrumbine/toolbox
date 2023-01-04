#!/usr/bin/env python3
import argparse
import glob
import os
import csv

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import netCDF4 as nc

import cartopy.crs as ccrs
import cartopy.feature as cfeature

matplotlib.use('agg')


#-------------------------------------------------------------
def getedge(fin, edgelons, edgelats):
    for line in fin:
        words=line.split(",")
        edgelats.append(float(words[1]))
        edgelons.append(float(words[0]))

    print("found ",len(edgelats), len(edgelons), "pts in edge file", flush=True)


#PlateCaree
#LambertConformal
#LambertCylindrical
#NorthPolarStereo

def plot_world_map(lons, lats, data, edgelons, edgelats):
    vmin = np.nanmin(data)
    vmax = np.nanmax(data)

    proj = ccrs.LambertConformal(central_longitude=-170, central_latitude=60., cutoff=25.)
    #proj = ccrs.NorthPolarStereo(true_scale_latitude=60.)
    #proj = ccrs.Stereographic(central_longitude=+170, central_latitude=60. )

    ax  = plt.axes(projection = proj)
    fig = plt.figure(figsize=(12, 9))
    ax  = fig.add_subplot(1, 1, 1, projection = proj)

    #ax.set_extent((-220,-120, 40, 90), crs=ccrs.PlateCarree())

    #Bering/okhotsk/some Beaufort/Chukchi
    ax.set_extent((-220,-145, 50, 70), crs=ccrs.PlateCarree())
    ax.gridlines(crs=ccrs.PlateCarree(), 
                 xlocs=[140., 150., 160., 170., -180, -170, -160, -150], 
                 ylocs=[45, 50, 55, 60, 66.6, 70, 75] )

    #'natural earth' -- coast only -- 
    ax.coastlines(resolution='10m')
    #ax.add_feature(cfeature.GSHHSFeature(levels=[1,2,3,4], scale="f") )

    plttitle = 'Plot of variable %s' % ("hello2")
    plt.title(plttitle)

    #Establish the color bar
    #colors=matplotlib.cm.get_cmap('jet')
    #colors=matplotlib.cm.get_cmap('gray')
    colors=matplotlib.cm.get_cmap('terrain')

# For gridded fields of 'data'
    #cs = ax.pcolormesh(lons, lats, data,vmin=vmin,vmax=vmax,cmap=colors, transform=ccrs.PlateCarree() )
    #cs = ax.pcolormesh(lons, lats, data,vmin=30.,vmax=vmax,cmap=colors, transform=ccrs.PlateCarree() )

    #cb = plt.colorbar(cs, extend='both', orientation='horizontal', shrink=0.5, pad=.04)
    #cbarlabel = '%s' % ("hello1")
    #cb.set_label(cbarlabel, fontsize=12)

# For a scatter plot of points:
    plt.scatter(edgelons, edgelats, transform=ccrs.PlateCarree(), s = 0.5, alpha = 0.5 )

# General

    plt.savefig("hello4.png")

    plt.close('all')

#----------------------------------------------------------------
lons = range(-360,360)
lats = range(-90,90)
data = np.zeros((len(lats),len(lons)))

for i in range(-360,360):
  data[:,i] = lats[:] 

edgelats = []
edgelons = []
fin = open("n.2022148.beta","r")
getedge(fin, edgelons, edgelats)

for i in range (0,1):
  print("i = ",i)
  plot_world_map(lons, lats, data, edgelons, edgelats)
  data += 1. 
