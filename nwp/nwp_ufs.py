import numpy as np
import numpy.ma as ma
from math import *

import networkx as netx
import netCDF4
from netCDF4 import Dataset

#--------------------------------------------------------------
#RTOFS:
#fin = Dataset("../dcom/rtofs_glo_2ds_f000_prog.nc","r")
#fin = Dataset("../dcom/rtofs_glo_2ds_f000_ice.nc","r")
#fin = Dataset("../dcom/rtofs_glo_2ds_f000_diag.nc","r")
#nx = len(fin.dimensions["X"])
#ny = len(fin.dimensions["Y"])
#lons = fin.variables["Longitude"][:,:]
#lats = fin.variables["Latitude"][:,:]
#sst  = fin.variables["ssh"][0,:,:]

#UFS:
fin = Dataset("grid_cice_NEMS_mx025.nc","r")
nx = len(fin.dimensions["ni"])
ny = len(fin.dimensions["nj"])
print(nx, ny)
#extract longitude, latitude, kmt
# -- node properties
# note that these are lat-lon of U points
lons = fin.variables["ulon"][:,:]
lats = fin.variables["ulat"][:,:]
lons *= (180./pi)
lats *= (180./pi)
# ocean fraction at T centers
kmt  = fin.variables["kmt"][:,:]

#--------------------------------------------------------------
print("lons: ",lons.max(), lons.min() )
print("lats: ",lats.max(), lats.min() )
print("kmt: ",kmt.max(), kmt.min(), flush=True )

#exit(0)

#--------------------------------------------------------------
#faster (~50 seconds) to used masked arrays than doubly nested loop (250 seconds)
#lmask = ma.masked_array(lons > 2.*360.+180.)

#ufs cice grid is -300 to 60, so don't need as many lon checks
lmask = ma.masked_array(lons < -180.)
lin = lmask.nonzero()
#debug print("180 lons ",len(lin), len(lin[0]), flush=True)
for k in range(0, len(lin[0])):
  i = lin[1][k]
  j = lin[0][k]
  lons[j,i] += 1.*360.
print("lons: ",lons.max(), lons.min() )

#exit(0)
#----------------------------------------------------------------
#print("nx,ny,nx*ny:",nx,ny,nx*ny)
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

#useful for checking where seam is
#tlat = 74.0
#for iii in range (0, 400):
#  ilon = -107.9 + 0.01*iii
#  (i,j) = find(lons, lats, ilon, tlat) 
#  print(i,j,tlat, ilon)

#start in Bering strait
(i_bering, j_bering) = find(lons, lats, -168.59, 65.68) #Bering Strait
#(i_bering, j_bering) = find(lons, lats, -126.0, 71.0) # S of banks island
#(i_bering, j_bering) = find(lons, lats, -124.0, 75.1) # N of banks island
#(i_bering, j_bering) = find(lons, lats, -103.0, 74.35) # Central passage
print("bering:",i_bering,j_bering)

#finish in ... Baffin Bay
#Lat = 74.0 N, -78.0 
(i_finish, j_finish) = find(lons, lats, -74.0, 74.0)
print("finish",i_finish, j_finish)

#exit(0)
#--------------------------------------------------------------

# Construct nodes -- limit area to keep run time manageable:
latmin = 65.0
latmax = 82.0
#lonmin = 185.0-360.
#lonmax = 290.0-360.
#-170 if starting from bering strait, -130 for the banks island paths
lonmin = -170.0
#lonmin = -130.0
lonmax =  -72.0
xmask = ma.masked_outside(lons, lonmin, lonmax)
xin = xmask.nonzero()
#debug print(len(xin), len(xin[0]), flush=True)
xmask = ma.logical_and(xmask, ma.masked_outside(lats, latmin, latmax))
xin = xmask.nonzero()
#debug print(len(xin), len(xin[0]), flush=True)

#xmask = ma.logical_and(xmask, sst < 1000.)
xmask = ma.logical_and(xmask, kmt > 0.)
xin = xmask.nonzero()
print("final set of points to consider",len(xin), len(xin[0]),flush=True)

#exit(0)


#Not a directed graph
G = netx.Graph()

nodemap = np.full((ny, nx),int(-1),dtype="int")
for k in range(0, len(xin[0])):
  i = xin[1][k]
  j = xin[0][k]
  if (k%15000 == 0):
    print("adding nodes, k = ",k, flush=True)
  #debug print("node:",k,i,j,lats[j,i], lons[j,i], kmt[j,i], flush=True)
  nodemap[j,i] = int(k)
  G.add_node(k, i = i, j =j, lat = lats[j,i], lon = lons[j,i], kmt=kmt[j,i] )
print("Done adding nodes, k=",k, flush=True)
#exit(0)

#---------------------------------------------------------
# RG: tripolar grid means adjacent geographic points aren't always i,j adjacent
# fix!
# Construct edges between nodes:
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
      G.add_edge(n, nodemap[j,im], weight = 1.)
  if (ip < nx):
    if (nodemap[j,ip] != -1):
      G.add_edge(n, nodemap[j,ip], weight = 1.)

  if (jp < ny ):
    if (nodemap[jp,i] != -1):
      G.add_edge(n, nodemap[jp,i], weight = 1.)
    if (im >= 0):
      if (nodemap[jp,im] != -1):
        G.add_edge(n, nodemap[jp,im], weight = 1.)
    if (ip < nx):
      if (nodemap[jp,ip] != -1):
        G.add_edge(n, nodemap[jp,ip], weight = 1.)
  #RG: a guess about the archipelago seam
  else:
    tmpi = i
    if (i < nx/2-1):
      tmpi = nx - 1 - i
    if (nodemap[j,tmpi] != -1):
      G.add_edge(n, nodemap[j,tmpi], weight = 1.)

  if (jm >= 0 ):
    if (nodemap[jm,i] != -1):
      G.add_edge(n, nodemap[jm,i], weight = 1.)
    if (im >= 0):
      if (nodemap[jm,im] != -1):
        G.add_edge(n, nodemap[jm,im], weight = 1.)
    if (ip < nx):
      if (nodemap[jm,ip] != -1):
        G.add_edge(n, nodemap[jm,ip], weight = 1.)

print("Have constructed graph, number of edges =",k, len(G.edges), flush=True)
#exit(0)


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
  print("still no path, Bering to Banks Island")
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
  #      flush=True )
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
kmlout.close()
      
exit(0)

#-----------------------------------------------------
#Prohibitive run time on 1/12th grid
#> 15 minutes on ufs 1.0 grid (banks-reduced domain)

print("finding all simple paths",flush=True)
paths = netx.all_simple_paths(G,start,finish)

k = 0
for x in paths :
  print(k,'path length ',len(x))
  k += 1
print("number of paths = ",k)

print(paths)

## count number of paths which pass through each grid cell
#counts = np.zeros((ny, nx),dtype="int")
