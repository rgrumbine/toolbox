import sys
import os
import datetime

from math import *
import numpy as np
import numpy.ma as ma

import netCDF4
from netCDF4 import Dataset

import networkx as netx

# User-written
from functions import *
from graphics import *

#--------------------------------------------------------
# define a subset to search within for paths
# NWP Domain:
latmin = 64.0
latmax = 82.0
lonmin = 185.0
lonmax = 290.0

def cafs_fname(base, tag):
    #PSL
    #fname = base+'/'+"/"+"REB2."+tag.strftime("%Y-%m-%d") + ".nc"
    #EMC
    fname = base+'/'+tag.strftime("%Y%m%d") +"/"+"REB2."+tag.strftime("%Y-%m-%d") + ".nc"
    return fname
#--------------------------------------------------------
base = os.environ['base']

tag = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]) )

fname = cafs_fname(base, tag)
# PSL
#if (not os.path.exists(base+'/'+"/"+fname) ):
#  print("could not open ",base+'/'+"/"+fname, flush=True)
# EMC
if (not os.path.exists(fname) ):
  print("could not open "+fname, flush=True)
  exit(1)

fin = Dataset(fname, "r")

nx = len(fin.dimensions["ni"])
ny = len(fin.dimensions["nj"])
lons = fin.variables["TLON"][:,:]
lats = fin.variables["TLAT"][:,:]
tarea = fin.variables["tarea"][:,:]

for tstep in range(0,40):
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

  # One may/must treat these fields as masked, as in masked arrays
  indices = tair.nonzero()

# flag is 1 = land, 0 = not-land
  land = np.zeros((ny,nx))
  land.fill(1)
  for k in range(0,len(indices[0]) ):
    j = indices[0][k]
    i = indices[1][k]
    land[j,i] = 0.0 

  #------- Universal -----------------------------------------
  # Construct nodes -- brute force looping over all grid points:
  # RG: Rtofs does this more elegantly, using masked arrays.
  #     The coarser and regional cafs grid doesn't demand this the way 
  #       the global, higher resolution RTOFS does
  offmap = 0
  nodemap = np.full((ny,nx),int(offmap), dtype="int")
 
  #Not a directed graph
  G = netx.Graph()
  
  #1 -> steps in i,j space
  #2 -> meters
  #3 -> weighted by polar class
  #4 -> weight by 1./(1.1-aice)
  cost_type = 4
  
  k = int(1)
  for i in range(0,nx):
    for j in range(0,ny):
      if (lats[j,i] > latmin and lats[j,i] < latmax and
          lons[j,i] > lonmin and lons[j,i] < lonmax     ):
        if (land[j,i] == 0):
          nodemap[j,i] = int(k)
          #n.b.: It is necessary to include explicit cast or the printing 
          #        lists np.float32(value) rather than value
          G.add_node(k, i = i, j =j, lat = float(lats[j,i]), lon = float(lons[j,i]),  aice= float(aice[j,i]), hi = float(hi[j,i]) )
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
        if (nodemap[j,im] != offmap):
          weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[j,im], lon2 = lons[j,im], aice = aice[j,i])
          G.add_edge(n, nodemap[j,im], weight= weight)
          k += 1
  
      if (ip < nx):
        if (nodemap[j,ip] != offmap):
          weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[j,ip], lon2 = lons[j,ip], aice = aice[j,i])
          G.add_edge(n, nodemap[j,ip], weight = weight)
          k += 1
  
      if (jp < ny ):
        if (nodemap[jp,i] != offmap):
          weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jp,i], lon2 = lons[jp,i], aice = aice[j,i])
          G.add_edge(n, nodemap[jp,i], weight = weight)
          k += 1
        if (im >= 0):
          if (nodemap[jp,im] != offmap):
            weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jp,im], lon2 = lons[jp,im], aice = aice[j,i])
            G.add_edge(n, nodemap[jp,im], weight = weight)
            k += 1
        if (ip < nx):
          if (nodemap[jp,ip] != offmap):
            weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jp,ip], lon2 = lons[jp,ip], aice = aice[j,i])
            G.add_edge(n, nodemap[jp,ip], weight = weight)
            k += 1
  
      if (jm >= 0 ):
        if (nodemap[jm,i] != offmap):
          weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jm,i], lon2 = lons[jm,i], aice = aice[j,i])
          G.add_edge(n, nodemap[jm,i], weight = weight)
          k += 1
        if (im >= 0):
          if (nodemap[jm,im] != offmap):
            weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jm,im], lon2 = lons[jm,im], aice = aice[j,i])
            G.add_edge(n, nodemap[jm,im], weight = weight)
            k += 1
        if (ip < nx):
          if (nodemap[jm,ip] != offmap):
            weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jm,ip], lon2 = lons[jm,ip], aice = aice[j,i])
            G.add_edge(n, nodemap[jm,ip], weight = weight)
            k += 1


  #--------------------------------------------------------
  #    Select start and finish points
  
  i_start, j_start = find(lons, lats, -168.59+360, 65.68)
  print("findij Bering strait ",i_start, j_start)
  i_finish, j_finish = find(lons, lats, -78.0+360, 74.0)
  print("findij Baffin Bay ",i_finish, j_finish, flush=True)
  
  # Quick check to see whether there are _any_ paths:
  start  = nodemap[j_start, i_start]
  finish = nodemap[j_finish, i_finish]
  print("Is there a path from start to finish? ",netx.has_path(G,start,finish ), flush=True )
  if (not netx.has_path(G,start,finish )):
    exit(1)

  #------------------------------------------------
  path = netx.dijkstra_path(G,start, finish)
  #debug: print("dijkstra length and score ", len(path), 
  #debug:        netx.dijkstra_path_length(G, start, finish), flush=True)
  pseudo_length = netx.dijkstra_path_length(G, start, finish)
  
  graphic_lats = np.zeros((len(path)))
  graphic_lons = np.zeros((len(path)))
  for k in range(0,len(path)):
    print(k,G.nodes[path[k]])
    graphic_lats[k] = G.nodes[path[k]]['lat']
    graphic_lons[k] = G.nodes[path[k]]['lon']
  print("",flush=True)
  
#----------- kml output ---------------------------------
  kmlout_path("path_"+tag.strftime("%Y%m%d")+"_"+"{:d}".format((tstep+1)*6)+".kml", G, path)

#----------- Graphics ---------------------------------
  show(graphic_lats, graphic_lons, tag, hours = (tstep+1)*6, cost = pseudo_length)
  del graphic_lats, graphic_lons

#-----------------------------------------------------
# RG: shapefile output
