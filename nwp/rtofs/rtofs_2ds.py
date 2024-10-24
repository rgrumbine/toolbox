import numpy as np
import numpy.ma as ma
from math import *
import datetime

import networkx as netx
import netCDF4
from netCDF4 import Dataset

#--------------------------------------------------------------
#fin = Dataset("../dcom/rtofs_glo_2ds_f000_prog.nc","r")
#fin = Dataset("../dcom/rtofs_glo_2ds_f000_diag.nc","r")

# cice_inst
#fin = Dataset("rtofs_glo.t00z.n00.cice_inst.nc","r")
#nx = len(fin.dimensions["ni"])
#ny = len(fin.dimensions["nj"])
#lons = fin.variables["TLON"][:,:]
#lats = fin.variables["TLAT"][:,:]
#sst   = fin.variables["sst"][0,:,:]
#aice  = fin.variables["aice"][0,:,:]

# 2ds_ice
fin = Dataset("rtofs_glo_2ds_f000_ice.nc","r")
nx = len(fin.dimensions['X'])
ny = len(fin.dimensions['Y'])
lons = fin.variables["Longitude"][:,:]
lats = fin.variables["Latitude"][:,:]
#not available: sst   = fin.variables["sst"][0,:,:]
aice  = fin.variables["ice_coverage"][0,:,:]
#debug: check distance of ice-free arctic  aice.fill(0.)

#debug:
print("lons: ",lons.max(), lons.min() )
print("lats: ",lats.max(), lats.min() )
print("aice: ",aice.max(), aice.min(), flush=True )

#exit(0)

#--------------------------------------------------------------
# Ensure lons are  <= 360.
#faster (~50 seconds) to used masked arrays than doubly nested loop (250 seconds)
if (lons.max() > 360. or lons.min() < -360. ):
  lmask = ma.masked_array(lons > 2.*360.+180.)
  lin = lmask.nonzero()
  for k in range(0, len(lin[0])):
    i = lin[1][k]
    j = lin[0][k]
    lons[j,i] -= 3.*360.
  #debug:
  print("lons: ",lons.max(), lons.min(), flush=True )
  
  lmask = ma.masked_array(lons > 1.*360.+180.)
  lin = lmask.nonzero()
  for k in range(0, len(lin[0])):
    i = lin[1][k]
    j = lin[0][k]
    lons[j,i] -= 2.*360.
  #debug:
  print("lons: ",lons.max(), lons.min(), flush=True )
  
  #most (10.6 million of 14.7 million) rtofs points have lons > 180, so subtract 360 and 
  # then correct the smaller number that are < -180 as a result
  lons -= 360.
  lmask = ma.masked_array(lons < -180.)
  lin = lmask.nonzero()
  #print("180 lons ",len(lin), len(lin[0]))
  for k in range(0, len(lin[0])):
    i = lin[1][k]
    j = lin[0][k]
    lons[j,i] += 1.*360.

if ( lons.max() > 180. ):
    lons -= 360.
#debug:
print("lons: ",lons.max(), lons.min(), flush=True )

#debug: for i in range(0,nx):
#debug:   print(i,lats[ny-1,i], lons[ny-1,i], lats[ny-2,i], lons[ny-2,i])
#debug: exit(0)

#----------------------------------------------------------------
from functions import *

#----------------------------------------------------------------

#tlat = 74.0
#for iii in range (0, 400):
#  ilon = -107.9 + 0.01*iii
#  (i,j) = find(lons, lats, ilon, tlat) 
#  print(i,j,tlat, ilon)

#start in Bering strait
(i_bering, j_bering) = find(lons, lats, -168.59, 65.68) #Bering Strait
#(i_bering, j_bering) = find(lons, lats, -126, 71.0) # S of banks island
#(i_bering, j_bering) = find(lons, lats, -124.0, 75.1) # N of banks island
#(i_bering, j_bering) = find(lons, lats, -103.0, 74.35) # Central passage
print("bering:",i_bering,j_bering, flush=True)

#finish in ... Baffin Bay
#Lat = 74.0 N, -78.0 
(i_finish, j_finish) = find(lons, lats, -74.0, 74.0)
print("finish",i_finish, j_finish, flush=True)

#debug: exit(0)
#--------------------------------------------------------------

# Construct nodes -- limit area to keep run time manageable:
latmin = 64.0
latmax = 82.0
#lonmin = 185.0-360.
#lonmax = 290.0-360.
lonmin = -175.0
lonmax =  -70.0
xmask = ma.masked_outside(lons, lonmin, lonmax)
xin = xmask.nonzero()
#debug: print(len(xin), len(xin[0]), flush=True)
xmask = ma.logical_and(xmask, ma.masked_outside(lats, latmin, latmax))
xin = xmask.nonzero()
#debug: 
print("number of points:", len(xin[0]), flush=True)

xmask = ma.logical_and(xmask, aice < 1000.)
xin = xmask.nonzero()
#debug: 
print("number of active points", len(xin[0]), flush=True)

#debug: exit(0)


#----------------------------- Begin Graph --------------------
#Not a directed graph
G = netx.Graph()

nodemap = np.full((ny, nx),int(-1),dtype="int")
for k in range(0, len(xin[0])):
  i = xin[1][k]
  j = xin[0][k]
  if (k%15000 == 0):
    print("adding nodes, k = ",k, flush=True)
  #debug print("node:",k,i,j,lats[j,i], lons[j,i], aice[j,i], flush=True)
  nodemap[j,i] = int(k)
  G.add_node(k, i = i, j =j, lat = lats[j,i], lon = lons[j,i], aice=aice[j,i] )
#debug:
print("Done adding nodes, k=",k, flush=True)
#debug: exit(0)

#---------------------------------------------------------
# RG: tripolar grid means adjacent geographic points aren't always i,j adjacent
# fix!
# Construct edges between nodes:

#cost_type = 
  #1 -> steps in i,j space
  #2 -> meters
  #3 -> weighted by polar class
  #4 -> weight by 1./(1.1-aice)
cost_type = 4

for k in range(0, len(xin[0])):
  i = xin[1][k]
  j = xin[0][k]
  jp = j + 1
  jm = j - 1
  ip = i + 1
  im = i - 1
  n = nodemap[j,i]
  if (n == -1):
    continue

  if (im >= 0):
    if (nodemap[j,im] != -1):
      weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], 
                               lat2 = lats[j,im], lon2 = lons[j,im], aice = aice[j,i])
      G.add_edge(n, nodemap[j,im], weight = weight)
  if (ip < nx):
    if (nodemap[j,ip] != -1):
      weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], 
                               lat2 = lats[j,ip], lon2 = lons[j,ip], aice = aice[j,i])
      G.add_edge(n, nodemap[j,ip], weight = weight)

  if (jp < ny ):
    if (nodemap[jp,i] != -1):
      weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jp,i], lon2 = lons[jp,i], aice = aice[j,i])
      G.add_edge(n, nodemap[jp,i], weight = weight)
    if (im >= 0):
      if (nodemap[jp,im] != -1):
        weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jp,im], lon2 = lons[jp,im], aice = aice[j,i])
        G.add_edge(n, nodemap[jp,im], weight = weight)
    if (ip < nx):
      if (nodemap[jp,ip] != -1):
        weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jp,ip], lon2 = lons[jp,ip], aice = aice[j,i])
        G.add_edge(n, nodemap[jp,ip], weight = weight)
  #RG: a guess about the archipelago seam
  else:
    tmpi = i
    if (i < nx/2-1):
      tmpi = nx - 1 - i
    if (nodemap[j,tmpi] != -1):
      G.add_edge(n, nodemap[j,tmpi], weight = 1.)

  if (jm >= 0 ):
    if (nodemap[jm,i] != -1):
      weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jm,i], lon2 = lons[jm,i], aice = aice[j,i])
      G.add_edge(n, nodemap[jm,i], weight = weight)
    if (im >= 0):
      if (nodemap[jm,im] != -1):
        weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jm,im], lon2 = lons[jm,im], aice = aice[j,i])
        G.add_edge(n, nodemap[jm,im], weight = weight)
    if (ip < nx):
      if (nodemap[jm,ip] != -1):
        weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jm,ip], lon2 = lons[jm,ip], aice = aice[j,i])
        G.add_edge(n, nodemap[jm,ip], weight = weight)

#debug:
print("Have constructed graph, number of nodes, edges =",k, len(G.edges), flush=True)
#debug: exit(0)


#--------------------------------------------------------------
start  = nodemap[j_bering, i_bering]
finish = nodemap[j_finish, i_finish]

print(i_bering, j_bering, i_finish, j_finish, start, finish, nodemap[j_bering, i_bering], nodemap[j_finish, i_finish], flush=True)

print(G.nodes[start])
print(G.nodes[finish])

print("Is there a path from start to finish? ",netx.has_path(G,start,finish ), flush=True )
if (not netx.has_path(G,start,finish )):
  (i_finish, j_finish) = find(lons, lats, -126, 71.0)
  #(i_finish, j_finish) = find(lons, lats, -103, 74.35)
  #orig (i_finish, j_finish) = find(lons, lats, -78.0, 74.0)
  #exit(1)
  print("retrying with ",i_finish, j_finish)
  finish = nodemap[j_finish, i_finish]

if (not netx.has_path(G, start, finish )):
  print("still no path, Bering to Banks Island, exiting", flush=True)
  exit(1)

path = netx.dijkstra_path(G,start, finish)

pseudo_length = netx.dijkstra_path_length(G,start, finish)

print("dijkstra length ", len(path), pseudo_length, flush=True)

tlons = np.zeros((len(path)))
tlats = np.zeros((len(path)))

for k in range(0,len(path)):
  print(k,G.nodes[path[k]])
  #print(k, 
  #      G.nodes[path[k]]['i'],
  #      G.nodes[path[k]]['j'],
  #      G.nodes[path[k]]['lon'],
  #      G.nodes[path[k]]['lat'],
  #      flush=True )
  tlons[k] = G.nodes[path[k]]['lon']
  tlats[k] = G.nodes[path[k]]['lat']

print("",flush=True)

#-------------------------------------------------------
kmlout = open("path.kml","w")
#Print header:
print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>", file=kmlout)
print("<kml xmlns=\"http://www.opengis.net/kml/2.2\" xmlns:gx=\"http://www.google.com/kml/ext/2.2\">", file=kmlout)
print("<Folder>", file=kmlout)
print("<LookAt>", file=kmlout)
print("  <range>3000000</range>", file=kmlout)
print("  <latitude> 68.0 </latitude>", file=kmlout)
print("  <longitude> -127</longitude>", file=kmlout)
print("</LookAt>", file=kmlout)
print("    <Document id=\"1\">", file=kmlout)

for k in range(0,len(path)):
  if (G.nodes[path[k]]['lon'] > 180.):
    tlon = G.nodes[path[k]]['lon']  - 360.
  else:
    tlon = G.nodes[path[k]]['lon'] 
  print("<Placemark> <Point> <coordinates>",tlon,G.nodes[path[k]]['lat'],0.0,
        "</coordinates></Point></Placemark>", file=kmlout)

#Print footer:
print("    </Document>",file=kmlout)
print("</Folder>",file=kmlout)
print("</kml>",file=kmlout)
      

#------------------------- Graphics -----------------------------
from graphics import *
tag=datetime.datetime(2024,10,18)
show(tlats, tlons, tag, hours=0, cost = pseudo_length) 
