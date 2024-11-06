#!/usr/bin/env python3
import argparse
import glob
import os
import csv

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeature

matplotlib.use('agg')


def mini(x,y, proj, ax, label="label",color='black'):
#  ax.plot(x,y, color=color, label=label)
  ax_accum.set_extent((-170, -75, 60, 80), crs=ccrs.PlateCarree())
  plt.scatter(x, y, transform=ccrs.PlateCarree(), s = 8, alpha = 0.5, color=color, label=label)

#---------------- sample info --------------------

nlon = int(360)
x = np.linspace(-175, -75, nlon)
y = np.linspace(55, 75, nlon)
z = np.linspace(65, 75, nlon)

#-------------- plotting / overplotting
#proj = ccrs.LambertConformal(central_longitude=-170, central_latitude=60., cutoff=25.)
proj = ccrs.LambertConformal(central_longitude = -120, central_latitude = 75., cutoff = 45.)

ax_accum  = plt.axes(projection = proj)
fig_accum = plt.figure(figsize=(12, 9))
ax_accum  = fig_accum.add_subplot(1, 1, 1, projection = proj)
#ax_accum.coastlines()
ax_accum.add_feature(cfeature.GSHHSFeature(levels=[1,2,3,4], scale="low") )

plttitle = 'Plot of variable %s' % ("hello2")
plt.title(plttitle)

#ax.gridlines(crs=ccrs.PlateCarree() )
ax_accum.gridlines(crs=ccrs.PlateCarree(),
  xlocs=[-225, -210, -195, -180, -165, -150, -135., -120, -105, -90,
          -75, -60, -45, -30, -15, 0, 15],
  ylocs=[60, 66.6, 70, 72.5, 75, 77.5, 80, 82.5, 85] )

#------------------

mini(x,y, proj, ax_accum, label="y", color = 'red')
mini(x,z, proj, ax_accum, label="z", color = 'blue')

#------------------

ax_accum.legend()
plt.savefig("hello5.png")
plt.close('all')

#----------------------------------------------------------------
