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

def show( tlats, tlons, tag, hours = 6, cost = 3482, reference = 3482):

  proj = ccrs.LambertConformal(central_longitude = 120, 
                               central_latitude = 75., cutoff = 45.)

  ax  = plt.axes(projection = proj)
  lll = 2.5
  fig = plt.figure(figsize=(lll*4, lll*3.8))
  ax  = fig.add_subplot(1, 1, 1, projection = proj)

  ax.set_extent((0, 210, 60, 80), crs=ccrs.PlateCarree())
  ax.gridlines(crs=ccrs.PlateCarree(),
      xlocs=[0, 30, 60, 90, 120, 150, 180, 210 ],
      ylocs=[60, 66.6, 70, 72.5, 75, 77.5, 80, 82.5, 85] )

  plt.annotate("NOAA/ESRL/PSL & CIRES/U. of Colorado: Experimental Sea Ice Forecasts", 
          (.05, .97), xycoords = 'figure fraction', size = 16 )
  plt.annotate("NOAA/NWS Environmental Modeling Center: Experimental Northeast Passage", 
          (.05, .94), xycoords = 'figure fraction', size = 16 )
  plt.annotate("Initial Date "+tag.strftime("%Y%m%d")+"  valid "+
          "{:d}".format(hours)+" hours ahead",
          (0.05, 0.91), xycoords = 'figure fraction', size = 16 ) 
  
  plt.annotate("Route cost "+"{:.0f}".format(cost)+" vs "
                            +"{:.0f}".format(reference)+" of completely ice-free path",
          (0.05, 0.88),  xycoords = 'figure fraction', size = 16 )
  plt.annotate("Cost is defined as 1.1/(1.1-Ai) – 1 at zero ice concentration.",(0.05, 0.835), xycoords = 'figure fraction', size = 16 )
  plt.annotate("For a completely ice-free route, the minimum penalty is 3482.",(0.05, 0.805), xycoords = 'figure fraction', size = 16 )
  plt.annotate("Any cost greater than this indicates at least some ice.",(0.05, 0.775), xycoords = 'figure fraction', size = 16 )
  plt.annotate("Costs can be over 10K in winter.",(0.05, 0.745), xycoords = 'figure fraction', size = 16 )
  plt.annotate("These northeast passage maps are suggestive, not actual guidance.",(0.05, 0.22), xycoords = 'figure fraction', size = 16 )
  plt.annotate("The passage displayed shows the least expensive path.",(0.05, 0.19), xycoords = 'figure fraction', size = 16 )
  plt.annotate("At this time, polar class of the ship is not considered.",(0.05, 0.16), xycoords = 'figure fraction', size = 16 )
  plt.annotate("Output fields from this diagnostic (including kml files) available by request.",(0.05, 0.13), xycoords = 'figure fraction', size = 16 )
  plt.annotate("Suggestions for improving the graphics are greatly welcome!",(0.05, 0.1), xycoords = 'figure fraction', size = 16 )
  plt.annotate("Please send display and support file suggestions to Robert.Grumbine@noaa.gov",(0.05, 0.07), xycoords = 'figure fraction', size = 16 )


  # scales are coarse, low, intermediate, high, and full
  ax.add_feature(cfeature.GSHHSFeature(levels = [1,2,3,4], scale = "low") )
                
  #plt.title("nep_"+tag.strftime("%Y%m%d")+"_00")
  
  plt.scatter(tlons, tlats, transform = ccrs.PlateCarree(),  
              marker = ".", s = 10, color = "purple")
  plt.savefig("nep_"+tag.strftime("%Y%m%d")+"_"+"{:03d}".format(hours)+".png")
##  plt.savefig("nep_"+"{:03d}".format(hours)+".png")
  
  plt.close('all')

