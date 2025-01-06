import sys
import os
from math import *
import datetime

import numpy as np
import numpy.ma as ma
import networkx as netx

import netCDF4
from netCDF4 import Dataset

# User-written
from functions import *

#Varies:
#NEP: from nep_graphics import *
#NWP: from graphics import *

#-------------------------------------------------

# Locations:
Bering_Strait = [-168.43, 65.46]

#NWP points
S_Banks_Island = [-126, 71.0]
N_Banks_Island = [-124.0, 75.1]
NWP_Central    = [-103.0, 74.35]
#NWP Terminus
Baffin_Bay = [-75.50, 73.97 ]

# NEP Terminus
Hammerfest = [ 21.4, 71.4 ]

Wrangel_Strait  = [ 178.0, 70.3 ]
S_Anzhu_Islands = [ 153.7, 73.1 ]
N_Anzhu_Islands = [ 154.3, 77.0 ]
S_Novaya_Zemlya = [  58.0, 70.4 ]
N_Novaya_Zemlya = [  68.9, 77.2 ]

#-------------------------------------------------

# Domain
# NWP
latmin =   64.0
latmax =   82.0
lonmin = -175.0
lonmax =  -70.0


# NEP domain
latmin =   64.0
latmax =   82.0
lonmin = -180.0
lonmax =  180.0

#--------------------------
# # dictionary
# # RTOFS - 2ds, CICE:
# nx: "X"
# ny: "Y"
# lats: "Latitude"
# lons: "Longitude"
# aice: "ice_coverage"
#
# # For RTOFS
# wrap_lons(lons)
#
# # UFS twelfth
# nx: "nlons"
# ny: "nlats"
# lons = "longitude"
# lats: "latitude"
# land: "land"
# dist: "distance"
#
# # UFS
# nx: "ni"
# ny: "nj"
# lons: "ulon"
# lats: "ulat"
# kmt: "kmt"   #ocean fraction at t centers


#--------------------------
# find starting point(lons, lats, lonin, latin):
# find finish point(lons, lats, lonin, latin):
# build mask (domain, lons, lats, xin, aice/kmt/...)
# make nodes (G, nodemap, xin, lats, lons, aice):
# add edges(G, nodemap, xin, tripolar?, ):
##  -- manage tripolar seam
# Loop over time
#   read in new guidance
#   edit/update properties of G
#   find path(start, finish, G, lons, lats, path, cost_type)
#   find pseudo-path length/cost, tlons/tlats
  #  kmlout
  #  graphics
  #  geopandas -- shapefile



