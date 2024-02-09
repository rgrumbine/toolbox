#!/u/robert.grumbine/env3.10/bin/python3
# python system
import os
import sys
import copy
from math import *
import datetime

# env libraries
import numpy as np
import numpy.ma as ma
import pygrib
import netCDF4

import pyproj

# shared
from match import *
from filtering import *
from tools import *

#---------------------------------------------------------------
#---------------------------------------------------------------
#                     Data Acquisition
# Read in the satellite obs to matchup -- satobs class in match file

#tb_lr = np.zeros((amsr2_lr.ntb))
#tb_hr = np.zeros((amsr2_hr.ntb))
#sat_lr = amsr2_lr()
#tmp = match(sat_lr)
tb_lr = np.zeros((match.amsr2_lr.ntb))
tb_hr = np.zeros((match.amsr2_hr.ntb))
sat_lr = match.amsr2_lr()

x = amsr2_lr(satid = 0, latitude = 0., longitude = 0.)
tmp = match.match(x)

allmatches = []
#read in sat obs (text file, from scan of bufr)
fin = open(sys.argv[1],"r")
k = int(0)
for line in fin:
  if ("lr" in line):
    k += int(1)
    #debug: if (k%1000 == 0):
    #debug:   print("k/1000 = ",k/1000)
    #RG: more efficient to work w. tmp directly? tmp.obs.read(line)
    x.read(line)
    tmp = match.match(x)
    allmatches.append(tmp)
    allmatches[k-1] = copy.deepcopy(tmp)
    #debug: if (k > 30000): break
    #debug: allmatches[k-1].show()

print(len(allmatches), "lr satellite obs")

#---------------------------------------------------------------
# Read in the ice fixed file (for distance to land, posteriori filter, ..)
# ice_distance, ice_land, ice_post, ice_latitude, ice_longitude
# Needs seaice_fixed_fields.nc in cwd

#fname='seaice_fixed_fields.nc'
#print("fname = ",fname)
from icefix import *
#debug: print(ice_post.max(), flush=True)

# Add ice fixed info to matchups (ice_land, ice_post, ice_distance)
#prep: 
for i in range(0,len(allmatches)):
  allmatches[i].add_icefix(ice_land, ice_post, ice_distance)
  #debug: allmatches[i].show()
del ice_land, ice_post, ice_distance

#debug: print("\n",allmatches[int(i/2)].obs.land, allmatches[int(i/2)].ice_land)
#debug: allmatches[int(i/2)].show()
#debug: exit(0)

#---------------------------------------------------------------
# Read ice analysis, add to matchup (icec)
analy_base='/u/robert.grumbine/noscrub/sice/sice.20240101/'
fname=analy_base+'seaice.t00z.5min.grb.grib2'
grbs = pygrib.open(fname)
for x in grbs:
  #debug: print(x.shortName, x.name, x.level, x.typeOfLevel, x.paramId, x.forecastTime, flush=True)
  #debug: print(x, flush=True)
  #placeholder: 
  print(x.values.max(), x.values.min(), flush=True )
icec = x.values

for i in range(0,len(allmatches)):
   allmatches[i].add_icec(icec)
   #debug:  if (i%1000 == 0):
   #debug:    allmatches[i].show()
del x, grbs

#debug: exit(0)

#---------------------------------------------------------------
# Read in IMS analysis, add to NH matchups
#ims_base='/u/robert.grumbine/noscrub/imstmp/'
#fname=ims_base+'ims2024038_4km_v1.3.nc'
from imsread import *

#debug: print("proj = ",pims, flush=True)
#debug: print("ims ", ims_value[3245,2321], flush=True)

# Add IMS to matchups
# Loop over observations, find nearest IMS point, append i+-1, j+-1 ims (5 total values)
# define an 'is ice' function, or 'partial ice'

for i in range(0,len(allmatches)):
  allmatches[i].add_ims(ims_value, pims)
  #debug: 
  allmatches[i].show()

#debug:
exit(0)

# For demo purposes, print out a patch around hibernia, say 80x80 around 46.5 N, 48.5 W 
#demo: (i,j) = ims_invlocate(pims, 46.5, 48.5)
#demo: print(i,j,"hibernia")
#demo: for dj in range (-40,40):
#demo:   for di in range (-40,40):
#demo:     print(ims_value[j+dj,i+di],end="")
#demo:   print("")


#---------------------------------------------------------------
# Use SST from qdoi v2, including its sea ice cover
# Read sst analysis, add sst and analysis' ice conc to match (sst, ice_sst)
sstbase='/u/robert.grumbine/static/oiv2/'
fname=sstbase+'oisst-avhrr-v02r01.20240101.nc'

sstgrid = nc.Dataset(fname, 'r', format='NETCDF4')
sst_nlats = len(sstgrid.dimensions["lat"])
sst_nlons = len(sstgrid.dimensions["lon"])

sst = np.zeros((sst_nlats, sst_nlons))
ice_sst = np.zeros((sst_nlats, sst_nlons))
#anom = np.zeros((sst_nlats, sst_nlons))
#err  = np.zeros((sst_nlats, sst_nlons))

sst   = sstgrid.variables["sst"][0,0,:,:]
ice_sst   = sstgrid.variables["ice"][0,0,:,:]
#anom  = sstgrid.variables["anom"] [0,0,:,:]
#err   = sstgrid.variables["err"][0,0,:,:]

for k in range(0,len(allmatches)):
  allmatches[k].add_oiv2(sst, ice_sst)
  #debug: 
  allmatches[i].show()

#debug: print("done adding in sst, max = ",sst.max(), flush=True)
exit(0)

#---------------------------------------------------------------
#  Now have all data in hand
#---------------------------------------------------------------

# experiment on ims and proj with lat-lon line -- Greenbelt and pts east
#x = amsr2_lr(satid = 0, latitude = 39., longitude = -77.)
#t2 = match.match(x)
#
##debug: print("ims_value ",ims_value, flush=True)
#longitude = -77.0
#for i in range(0,100):
#  t2.obs.longitude = longitude + i/10.0
#  t2.add_ims(ims_value, pims)
#  print(t2.obs.longitude, t2.ims)
