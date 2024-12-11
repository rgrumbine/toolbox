import sys
import os
import datetime

from math import *
import numpy as np
import numpy.ma as ma

#debug: import netCDF4
#debug: from netCDF4 import Dataset
#debug: import networkx as netx

# Graphics
import matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

matplotlib.use('Agg') #for batch mode
#matplotlib.use('Qt5Agg') #for interactive mode

def show( tlats, tlons, tag, hours = 6, cost = 2965, reference = 2965):

  proj = ccrs.LambertConformal(central_longitude = -120, 
                               central_latitude = 75., cutoff = 45.)

  ax_show  = plt.axes(projection = proj)
  lll = 2.5
  fig_show = plt.figure(figsize=(lll*4, lll*3))
  ax_show  = fig_show.add_subplot(1, 1, 1, projection = proj)

  ax_show.annotate("NOAA/ESRL/PSL & CIRES/U. of Colorado: Experimental Sea Ice Model", 
          (.05, .975), xycoords = 'figure fraction', size = 16 )
  ax_show.annotate("NOAA/NWS Environmental Modeling Center: Experimental Northwest Passage", 
          (.05, .94), xycoords = 'figure fraction', size = 16 )
  ax_show.annotate("Initial Date "+tag.strftime("%Y%m%d")+"  valid "+
          "{:d}".format(hours)+" hours ahead",
          (0.05, 0.905), xycoords = 'figure fraction', size = 16 ) 
  

  ax_show.annotate("route cost "+"{:.0f}".format(cost)+" vs "
                            +"{:.0f}".format(reference)+" of completely ice-free path",
          (0.125, 0.10),  xycoords = 'figure fraction', size = 24 )

  ax_show.set_extent((-170, -75, 60, 80), crs=ccrs.PlateCarree())
  
  ax_show.gridlines(crs=ccrs.PlateCarree(),
      xlocs=[-225, -210, -195, -180, -165, -150, -135., -120, -105, -90, 
              -75, -60, -45, -30, -15, 0, 15],
      ylocs=[60, 66.6, 70, 72.5, 75, 77.5, 80, 82.5, 85] )

  # scales are coarse, low, intermediate, high, and full
  ax_show.add_feature(cfeature.GSHHSFeature(levels = [1,2,3,4], scale = "low") )
                
  ax_show.scatter(tlons, tlats, transform = ccrs.PlateCarree(),  
              marker = ".", s = 10, color = "purple")
  
  fig_show.savefig("nwp_"+tag.strftime("%Y%m%d")+"_"+"{:03d}".format(hours)+".png")
  plt.close(fig_show)
  del ax_show, fig_show
