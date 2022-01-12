import numpy as np
from math import *

import networkx as netx
import netCDF4
from netCDF4 import Dataset

#--------------------------------------------------------------
fin = Dataset("seaice_fixed_fields.nc","r")
nx = len(fin.dimensions["nlons"])
ny = len(fin.dimensions["nlats"])
print(nx, ny)
#extract longitude, latitude, land, distance_to_land
# -- node properties
#longitude, latitude, land, distance_to_land
lons = fin.variables["longitude"][:,:]
lats = fin.variables["latitude"][:,:]
land = fin.variables["land"][:,:]
dist = fin.variables["distance_to_land"][:,:]

#print("lons: ",lons.max(), lons.min() )
#print("lats: ",lats.max(), lats.min() )
#print("land: ",land.max(), land.min() )
#print("dist: ",dist.max(), dist.min(), flush=True )

nodemap = np.zeros((ny, nx),dtype="int")

#--------------------------------------------------------------

# Construct nodes:

latmin = 64.0
latmax = 80.0
lonmin = 185.0
lonmax = 290.0

k = int(1)
#Not a directed graph
G = netx.Graph()
for i in range(0,nx):
  if (i%480 == 0):
    print("adding nodes, i = ",i, flush=True)
  for j in range(0,ny):
    if (lats[j,i] > latmin and lats[j,i] < latmax and 
        lons[j,i] > lonmin and lons[j,i] < lonmax     ):
      if (land[j,i] == 0):
        nodemap[j,i] = int(k)
        G.add_node(k, i = i, j =j, lat = lats[j,i], lon = lons[j,i],  land=land[j,i])
        k += int(1)
print("Done adding nodes, k=",k, flush=True)

# Construct edges between nodes:

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
        G.add_edge(n, nodemap[j,im], weight=0.)
        k += 1
    if (ip < nx):
      if (nodemap[j,ip] != 0):
        G.add_edge(n, nodemap[j,ip], weight = 0.)
        k += 1

    if (jp < ny ):
      if (nodemap[jp,i] != 0):
        G.add_edge(n, nodemap[jp,i], weight = 1.)
        k += 1
      if (im >= 0):
        if (nodemap[jp,im] != 0):
          G.add_edge(n, nodemap[jp,im], weight = 1.)
          k += 1
      if (ip < nx):
        if (nodemap[jp,ip] != 0):
          G.add_edge(n, nodemap[jp,ip], weight = 1.)
          k += 1

    if (jm >= 0 ):
      if (nodemap[jm,i] != 0):
        G.add_edge(n, nodemap[jm,i], weight = 1.)
        k += 1
      if (im >= 0):
        if (nodemap[jm,im] != 0):
          G.add_edge(n, nodemap[jm,im], weight = 1.)
          k += 1
      if (ip < nx):
        if (nodemap[jm,ip] != 0):
          G.add_edge(n, nodemap[jm,ip], weight = 1.)
          k += 1

print("Have constructed graph, number of edges =",k, len(G.edges), flush=True)

#--------------------------------------------------------------
#start in Bering strait
#Lat = 65.68, Lon = -168.59
i_bering = int(0.5 + (360. - 168.59)*12.) 
j_bering = int(0.5 + (90.0 -  65.68)*12.) 
#finish in ... Baffin Bay
#Lat = 74.0 N, -78.0 
i_finish = int(0.5 + (360. - 78.0)*12.) 
j_finish = int(0.5 + (90.0 - 74.0)*12.) 

start  = nodemap[j_bering, i_bering]
finish = nodemap[j_finish, i_finish]
#print(G.nodes[start])
#print(G.nodes[finish])
print(i_bering, j_bering, i_finish, j_finish, start, finish)
print("Is there a path from start to finish? ",netx.has_path(G,start,finish ), flush=True )
if (not netx.has_path(G,start,finish )):
  exit(1)

path = netx.dijkstra_path(G,start, finish)
print("dijkstra length ", len(path), flush=True)
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

kmlout = open("path.kml","w")
#RG: Need header and footer information
for k in range(0,len(path)):
  if (G.nodes[path[k]]['lon'] > 180.):
    tlon = G.nodes[path[k]]['lon']  - 360.
  else:
    tlon = G.nodes[path[k]]['lon'] 
  print("<Placemark> <Point> <coordinates>",tlon,G.nodes[path[k]]['lat'],0.0,
        "</coordinates></Point></Placemark>", file=kmlout)
      

#-----------------------------------------------------
exit(0)

#Prohibitive run time on 1/12th grid

print("finding all simple paths",flush=True)
paths = netx.all_simple_paths(G,start,finish)

k = 0
for x in paths :
  print(len(x))
  k += 1
print("number of paths = ",k)

print(paths)

# count number of paths which pass through each grid cell
counts = np.zeros((ny, nx),dtype="int")
