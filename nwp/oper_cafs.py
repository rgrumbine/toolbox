import sys
import os
import datetime

from math import *
import numpy as np
import numpy.ma as ma

import netCDF4
from netCDF4 import Dataset

import networkx as netx

import matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

#--------------------------------------------------------
def find(lons, lats, lonin, latin):
  #debug print("lon, lat in:",lonin, latin, flush=True)
  tmpx = lons - lonin
  tmpy = lats - latin
  #debug print("x ",tmpx.max(), tmpx.min(), lons.max(), lons.min(), flush=True )

  xmask = ma.masked_outside(tmpx, -0.5, 0.5)
  xin = xmask.nonzero() 
  wmask = ma.logical_and(xmask, ma.masked_outside(tmpy, +0.5, -0.5) )
  win = wmask.nonzero()

  imin = -1 
  jmin = -1
  dxmin = 999.
  dymin = 999.
  dmin  = 999.
  for k in range(0, len(win[0]) ):
    i = win[1][k]
    j = win[0][k] 
    #debug print(k,i,j,abs(tmpx[j,i]), abs(tmpy[j,i]), dxmin, dymin, dmin, flush=True)
    #if (abs(tmpx[j,i]) < dxmin and abs(tmpy[j,i]) < dymin):
    if (sqrt(tmpx[j,i]**2 + tmpy[j,i]**2) < dmin):
      imin = i
      jmin = j
      dxmin = abs(tmpx[j,i])
      dymin = abs(tmpy[j,i])
      dmin  = sqrt(tmpx[j,i]**2 + tmpy[j,i]**2)
  #print("dmin:",imin, jmin, dmin, dxmin, dymin)
  return (imin,jmin)
#--------------------------------------------------------
# Polar ship class
#debug: PC = int(input("What is the polar class of the ship vessel? (1-7)\n"))
PC = 1
PossAnswers = [1, 2, 3, 4, 5, 6, 7]
if(PC not in PossAnswers):
  raise Exception("Please select an answer between 1 and 7.")

def calculateCost(PolarClass, iceCon, iceThick):
    #RIO = (aice*10)RV
    #If aice <= .1, return 0
    #If RIO < 0, return 99999
    cost = 1
    return 1.

    #Considered Ice-Free
    if(iceCon <= .1):
        return 0

    if(PolarClass == 1 or PolarClass == 2 or PolarClass == 3 or PolarClass == 4):
        if(iceThick <= 70):
            cost = 3*(iceCon * 10)
        elif(iceThick <= 120):
            cost = 2*(iceCon * 10)
        else:
            cost = (iceCon * 10)
    elif(PolarClass == 5 or PolarClass == 6):
        if(iceThick <= 70):
            cost = 3*(iceCon * 10)
        elif(iceThick <= 95):
            cost = 2*(iceCon * 10)
        elif(iceThick <= 120):
            cost = iceCon*10
        else:
            return 999
    else:
        if(iceThick <= 30):
            cost = 3*(iceCon * 10)
        elif(iceThick <= 50):
            cost = 2*(iceCon * 10)
        elif(iceThick <= 70):
            cost = iceCon*10
        else:
            return 999
    return cost

#Calculates the distance of two points based on the longitude and latitude points of each point
def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    earth_radius = 6371

    # Convert latitude and longitude from degrees to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Calculate the distance
    distance = earth_radius * c

    return distance

def cost(case, lat1 = 0, lon1 = 0, lat2 = 0, lon2 = 0, i1 = 0, j1 = 0, i2 = 0, j2 = 0, aice = 0, hi = 0):
  if (case == 1):
    return 1.
  elif (case == 2):
    if (lon1 == 0 and lat1 == 0 and lon2 == 0 and lat2 == 0):
      print("Must give lat,lon of points to compute distance weighting")
      return 1
    else:
      return calculate_distance(lat1, lon1, lat2, lon2)
  elif (case == 3):
    if (i1 == 0 and i2 == 0 and j1 == 0 and j2 == 0):
      print("Must give i,j of points when weighting by polar class")
      return 1
    else:
      return 1 #RG: temporary
  elif (case == 4):
    if (lon1 == 0 and lat1 == 0 and lon2 == 0 and lat2 == 0):
      print("Must give lat,lon of points to compute area-distance weighting")
      return 1.
    else:
      return 1.1*calculate_distance(lat1, lon1, lat2, lon2) / (1.1 - aice)

  else:
    print("unknown case, =",case)
    return 1


#--------------------------------------------------------
base = "/home/Robert.Grumbine/clim_data/cafs/"

#tag = datetime.datetime(2022,4,1)
#debug: print("args ",sys.argv, flush=True)
tag = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]) )

dname = tag.strftime("%Y%m%d")
fname = "REB2."+tag.strftime("%Y-%m-%d") + ".nc"
if (not os.path.exists(base+dname+"/"+fname) ):
  print("could not open ",base+dname+"/"+fname)
  exit(1)

fin = Dataset(base+dname+"/"+fname, "r")
nx = len(fin.dimensions["ni"])
ny = len(fin.dimensions["nj"])
lons = fin.variables["TLON"][:,:]
lats = fin.variables["TLAT"][:,:]
tarea = fin.variables["tarea"][:,:]


#for tstep in range(0,40):
for tstep in range(0,1):
  aice = fin.variables["aice_h"][tstep,:,:]
  hs   = fin.variables["hs_h"][tstep,:,:]
  hi   = fin.variables["hi_h"][tstep,:,:]
  uvel = fin.variables["uvel_h"][tstep,:,:]
  vvel = fin.variables["vvel_h"][tstep,:,:]
  tsfc = fin.variables["Tsfc_h"][tstep,:,:]
  uatm = fin.variables["uatm_h"][tstep,:,:]
  vatm = fin.variables["vatm_h"][tstep,:,:]
  sst  = fin.variables["sst_h"][tstep,:,:]
  sss  = fin.variables["sss_h"][tstep,:,:]
  tair = fin.variables["Tair_h"][tstep,:,:]
  aice = fin.variables["aice_h"][tstep,:,:]
  aice = fin.variables["aice_h"][tstep,:,:]

  #debug: print("sample for tstep ",tstep,aice.max(), aice.min(), 
  #debug:                tsfc.max(), sst.max(), tair.max() )

  # One may/must treat these fields as masked, as in masked arrays
  indices = tair.nonzero()
  #debug: print(len(indices), len(indices[0]), flush=True )

# flag is 1 = land, 0 = not-land
  land = np.zeros((ny,nx))
  land.fill(1)
  for k in range(0,len(indices[0]) ):
    j = indices[0][k]
    i = indices[1][k]
    land[j,i] = 0.0 

#--------------------------------------------------------
# define a subset to search within for paths
latmin = 64.0
latmax = 80.0
lonmin = 185.0
lonmax = 290.0

# Construct nodes -- brute force looping over all grid points:
nodemap = np.zeros((ny,nx),dtype="int")

k = int(1)
#Not a directed graph
G = netx.Graph()

#1 -> steps in i,j space
#2 -> meters
#3 -> weighted by polar class
#4 -> weight by 1./(1.1-aice)
cost_type = 4

for i in range(0,nx):
  for j in range(0,ny):
    #debug: if (k%1000 == 0):
      #debug: print("adding nodes, i = ",i, flush=True)
    if (lats[j,i] > latmin and lats[j,i] < latmax and
        lons[j,i] > lonmin and lons[j,i] < lonmax     ):
      if (land[j,i] == 0):
        nodemap[j,i] = int(k)
        G.add_node(k, i = i, j =j, lat = lats[j,i], lon = lons[j,i],  land=land[j,i])
        k += int(1)
#debug: print("Done adding nodes, k=",k, flush=True)

# Construct edges between nodes
k = 0
for j in range(0,ny):
  jp = j + 1
  jm = j - 1
  for i in range(0,nx):
    ip = i+1
    im = i-1
    if (not (lats[j,i] > latmin and lats[j,i] < latmax and
             lons[j,i] > lonmin and lons[j,i] < lonmax     )    ):
      continue
    n = nodemap[j,i]
    if (n == 0):
      continue

    if (im >= 0):
      if (nodemap[j,im] != 0):
        weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[j,im], lon2 = lons[j,im], aice = aice[j,i])
        G.add_edge(n, nodemap[j,im], weight= weight)
        k += 1

    if (ip < nx):
      if (nodemap[j,ip] != 0):
        weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[j,ip], lon2 = lons[j,ip], aice = aice[j,i])
        G.add_edge(n, nodemap[j,ip], weight = weight)
        k += 1

    if (jp < ny ):
      if (nodemap[jp,i] != 0):
        weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jp,i], lon2 = lons[jp,i], aice = aice[j,i])
        G.add_edge(n, nodemap[jp,i], weight = weight)
        k += 1
      if (im >= 0):
        if (nodemap[jp,im] != 0):
          weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jp,im], lon2 = lons[jp,im], aice = aice[j,i])
          G.add_edge(n, nodemap[jp,im], weight = weight)
          k += 1
      if (ip < nx):
        if (nodemap[jp,ip] != 0):
          weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jp,ip], lon2 = lons[jp,ip], aice = aice[j,i])
          G.add_edge(n, nodemap[jp,ip], weight = weight)
          k += 1

    if (jm >= 0 ):
      if (nodemap[jm,i] != 0):
        weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jm,i], lon2 = lons[jm,i], aice = aice[j,i])
        G.add_edge(n, nodemap[jm,i], weight = weight)
        k += 1
      if (im >= 0):
        if (nodemap[jm,im] != 0):
          weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jm,im], lon2 = lons[jm,im], aice = aice[j,i])
          G.add_edge(n, nodemap[jm,im], weight = weight)
          k += 1
      if (ip < nx):
        if (nodemap[jm,ip] != 0):
          weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jm,ip], lon2 = lons[jm,ip], aice = aice[j,i])
          G.add_edge(n, nodemap[jm,ip], weight = weight)
          k += 1

#debug: print("Have constructed graph, number of edges =",k, len(G.edges), flush=True)
#debug: exit(0)

#--------------------------------------------------------
#    Select start and finish points

##start in Bering strait
##Lat = 65.68, Lon = -168.59
#i_start = int(0.5 + (360. - 168.59)*12.)
#j_start = int(0.5 + (90.0 -  65.68)*12.)
##finish in ... Baffin Bay
##Lat = 74.0 N, -78.0
#i_finish = int(0.5 + (360. - 78.0)*12.)
#j_finish = int(0.5 + (90.0 - 74.0)*12.)

#for j in range(0,ny):
#  for i in range(0, nx):
#      print(i, j, nodemap[j,i])
# nodemap = 0 when i,j not in map

#exit(0)

# cafs grid is different
#RG: Need a findij function (65.68 N, -168.59), (64.0, -78.0) 
#RG: is baffin bay insize cafs domain?
i_start = int(287)
j_start = int(67)
#i_finish = int(415)
#j_finish = int(420)
i_finish = int(396) 
j_finish = int(344) 
#debug: print("start: ",lons[j_start, i_start], lats[j_start, i_start] )
#debug: print("finis: ",lons[j_finish, i_finish], lats[j_finish, i_finish] )

# Quick check to see whether there are _any_ paths:
start  = nodemap[j_start, i_start]
finish = nodemap[j_finish, i_finish]
#debug: print("start node ",G.nodes[start])
#debug: print("finish node ",G.nodes[finish])
#debug: print(i_start, j_start, i_finish, j_finish, start, finish)
print("Is there a path from start to finish? ",netx.has_path(G,start,finish ), flush=True )
if (not netx.has_path(G,start,finish )):
  exit(1)

#------------------------------------------------
path = netx.dijkstra_path(G,start, finish)
print("dijkstra length and score ", len(path), 
       netx.dijkstra_path_length(G, start, finish), flush=True)

for k in range(0,len(path)):
  print(k,G.nodes[path[k]])
  #print(k,
  #      G.nodes[path[k]]['i'],
  #      G.nodes[path[k]]['j'],
  #      G.nodes[path[k]]['lon'],
  #      G.nodes[path[k]]['lat'],
  #      G.nodes[path[k]]['land'],
  #      flush=True )
print("",flush=True)
tlons = np.zeros((len(path)))
tlats = np.zeros((len(path)))

kmlout = open("path_"+tag.strftime("%Y%m%d")+"_00.kml","w")
#RG: Need header and footer information
for k in range(0,len(path)):
#  if (G.nodes[path[k]]['lon'] > 180.):
#    tlon = G.nodes[path[k]]['lon']  - 360.
#    tlons[k] = tlon
#  else:
  tlon = G.nodes[path[k]]['lon']
  tlons[k] = tlon
  tlats[k] = G.nodes[path[k]]['lat']
  print("<Placemark> <Point> <coordinates>",tlon,G.nodes[path[k]]['lat'],0.0,
        "</coordinates></Point></Placemark>", file=kmlout)

  #debug: exit(0)
#-----------------------------------------------------

# something not behaving with the geographic plotting:

matplotlib.use('Agg') #for batch mode
#matplotlib.use('Qt5Agg') #for interactive mode

proj = ccrs.LambertConformal(central_longitude = -120, central_latitude = 75., cutoff = 45.)

ax  = plt.axes(projection = proj)
lll = 2.5
fig = plt.figure(figsize=(lll*4, lll*3))
ax  = fig.add_subplot(1, 1, 1, projection = proj)

ax.set_extent((-170, -75, 60, 80), crs=ccrs.PlateCarree())

ax.gridlines(crs=ccrs.PlateCarree(),
    xlocs=[-225, -210, -195, -180, -165, -150, -135., -120, -105, -90, 
            -75, -60, -45, -30, -15, 0, 15],
    #ylocs=[50, 60, 66.6, 70, 75, 80] )
    ylocs=[60, 66.6, 70, 72.5, 75, 77.5, 80, 82.5, 85] )

                
ax.add_feature(cfeature.GSHHSFeature(levels = [1,2,3,4], scale = "l") )
                
plt.title("nwp_"+tag.strftime("%Y%m%d")+"_00")

plt.scatter(tlons, tlats, transform = ccrs.PlateCarree(),  marker = ".", s = 8, color = "purple")
plt.savefig("nwp_"+tag.strftime("%Y%m%d")+"_00.png")

plt.close('all')

exit(0)
#-----------------------------------------------------

#brute force looking for i,j to start/finish

indices = tair.nonzero()
for k in range(0,len(indices[0]) ):
  j = indices[0][k]
  i = indices[1][k]
  if ( (lons[j,i] > 280 or lons[j,i] < -80.0) and 
       (lons[j,i] < 320) and
       (lats[j,i] < 80 and lats[j,i] > 65.0) and
       aice[j,i] < 0.02):
    print("land ",i,j,lons[j,i], lats[j,i], aice[j,i], tair[j,i], hi[j,i])


exit(0)
#-----------------------------------------------------
# Greater than 10 m on cafs grid

#Prohibitive run time on 1/12th grid:

print("finding all simple paths",flush=True)
paths = netx.all_simple_paths(G,start,finish)

k = 0
for x in paths :
  print(len(x))
  k += 1
print("number of paths = ",k)

print(paths)

## count number of paths which pass through each grid cell
#counts = np.zeros((ny, nx),dtype="int")

