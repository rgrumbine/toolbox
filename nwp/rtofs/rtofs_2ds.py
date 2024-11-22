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
from graphics import *

# semi-universal constants -------------------------------------
# limit domain to keep run time manageable -- NWP domain
latmin = 64.0
latmax = 82.0
#lonmin = 185.0-360.
#lonmax = 290.0-360.
lonmin = -175.0
lonmax =  -70.0

#---------- somewhat particular to model -------------------------------------
base = os.environ['base']
tag = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]) )


# RG: auxiliary file with tmask, tarea for rtofs grid(s)
# RG: auxiliary file with lats, lons wrapped in to range

#fin = Dataset("../dcom/rtofs_glo_2ds_f000_prog.nc","r")
#fin = Dataset("../dcom/rtofs_glo_2ds_f000_diag.nc","r")

# cice_inst as data source:
#fin = Dataset("rtofs_glo.t00z.n00.cice_inst.nc","r")
#nx = len(fin.dimensions["ni"])
#ny = len(fin.dimensions["nj"])
#lons = fin.variables["TLON"][:,:]
#lats = fin.variables["TLAT"][:,:]
#sst   = fin.variables["sst"][0,:,:]
#aice  = fin.variables["aice"][0,:,:]

# RG: define a function to take date and hour, return file name
def rtofs_fname(base, tag, hhh):
  fname = base+"/rtofs."+tag.strftime("%Y%m%d")+ "/rtofs_glo_2ds_f"+"{:03d}".format(hhh)+"_ice.nc"
  return fname

# RG: define dictionary for nx, ny, lats, lons, aice -- moddef as for gross checks

# 2ds_ice
#---------- loop over model's time span -------------------------------------
hhh=000
for hhh in range (0, 193, 6):
  #fname = base+"/rtofs."+tag.strftime("%Y%m%d")+ "/rtofs_glo_2ds_f"+"{:03d}".format(hhh)+"_ice.nc"
  fname = rtofs_fname(base, tag, hhh)

  try:
    fin = Dataset(fname,"r")
  except:
    print("Could not open ",fname, flush=True)
    exit(1)

  if (hhh == 0):
    nx = len(fin.dimensions['X'])
    ny = len(fin.dimensions['Y'])
    lats = fin.variables["Latitude"][:,:]
    lons = fin.variables["Longitude"][:,:]
    # Ensure lons are  <= 360.
    wrap_lons(lons)
    #debug: print("lons: ",lons.max(), lons.min() )
    #debug: print("lats: ",lats.max(), lats.min(), flush=True )
  
  #not available in 2ds_ice: sst   = fin.variables["sst"][0,:,:]
  aice  = fin.variables["ice_coverage"][0,:,:]
  #debug: print("aice: ",aice.max(), aice.min(), flush=True )

  #debug: exit(0)
  #debug: check distance of ice-free arctic  -- cost_type = 2

  #----------------------------------------------------------------
  #start in Bering strait
  (i_bering, j_bering) = find(lons, lats, -168.59, 65.68) #Bering Strait
  #(i_bering, j_bering) = find(lons, lats, -126, 71.0) # S of banks island
  #(i_bering, j_bering) = find(lons, lats, -124.0, 75.1) # N of banks island
  #(i_bering, j_bering) = find(lons, lats, -103.0, 74.35) # Central passage
  print("bering:",i_bering,j_bering, flush=True)
  
  #finish in ... Baffin Bay
  (i_finish, j_finish) = find(lons, lats, -74.0, 74.0)
  print("finish",i_finish, j_finish, flush=True)
  
  #debug: exit(0)
  #--------------------------------------------------------------
  # Mask out areas outside NWP domain
  xmask = ma.masked_outside(lons, lonmin, lonmax)
  xin = xmask.nonzero()
  #debug: print('lons',len(xin), len(xin[0]), flush=True)
  xmask = ma.logical_and(xmask, ma.masked_outside(lats, latmin, latmax))
  #debug: xin = xmask.nonzero()
  #debug: print("number of points:", len(xin[0]), flush=True)
  # Also mask out nonvalues in aice
  xmask = ma.logical_and(xmask, aice < 1000.)
  xin = xmask.nonzero()
  #debug: print("number of active points", len(xin[0]), flush=True)
  #debug: exit(0)

  #----------------------------- Begin Graph --------------------
  #Not a directed graph
  G = netx.Graph()
  
  offmap = -1
  nodemap = np.full((ny, nx),int(offmap),dtype="int")
  for k in range(0, len(xin[0])):
    i = xin[1][k]
    j = xin[0][k]
    #debug:
    if (k%50000 == 0):
      print("adding nodes, k = ",k, flush=True)
    #debug print("node:",k,i,j,lats[j,i], lons[j,i], aice[j,i], flush=True)
    nodemap[j,i] = int(k)
    G.add_node(k, i = i, j =j, lat = lats[j,i], lon = lons[j,i], aice=aice[j,i] )
  #debug:
  print("Done adding nodes, k=",k, flush=True)
  #debug: exit(0)

  #---------- Universal --------------------------------------
  # Construct edges between nodes:
  
  #cost_type = 
    #1 -> steps in i,j space
    #2 -> meters
    #3 -> weighted by polar class
    #4 -> weight by 1.1/(1.1-aice)
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
      if (nodemap[j,im] != offmap):
        weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], 
                                 lat2 = lats[j,im], lon2 = lons[j,im], aice = aice[j,i])
        G.add_edge(n, nodemap[j,im], weight = weight)
    if (ip < nx):
      if (nodemap[j,ip] != offmap):
        weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], 
                                 lat2 = lats[j,ip], lon2 = lons[j,ip], aice = aice[j,i])
        G.add_edge(n, nodemap[j,ip], weight = weight)
  
    if (jp < ny ):
      if (nodemap[jp,i] != offmap):
        weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jp,i], lon2 = lons[jp,i], aice = aice[j,i])
        G.add_edge(n, nodemap[jp,i], weight = weight)
      if (im >= 0):
        if (nodemap[jp,im] != offmap):
          weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jp,im], lon2 = lons[jp,im], aice = aice[j,i])
          G.add_edge(n, nodemap[jp,im], weight = weight)
      if (ip < nx):
        if (nodemap[jp,ip] != offmap):
          weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jp,ip], lon2 = lons[jp,ip], aice = aice[j,i])
          G.add_edge(n, nodemap[jp,ip], weight = weight)
    #RG: a guess about the archipelago seam
    else:
      tmpi = i
      if (i < nx/2-1):
        tmpi = nx - 1 - i
      if (nodemap[j,tmpi] != offmap):
        G.add_edge(n, nodemap[j,tmpi], weight = 1.)
  
    if (jm >= 0 ):
      if (nodemap[jm,i] != offmap):
        weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jm,i], lon2 = lons[jm,i], aice = aice[j,i])
        G.add_edge(n, nodemap[jm,i], weight = weight)
      if (im >= 0):
        if (nodemap[jm,im] != offmap):
          weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jm,im], lon2 = lons[jm,im], aice = aice[j,i])
          G.add_edge(n, nodemap[jm,im], weight = weight)
      if (ip < nx):
        if (nodemap[jm,ip] != offmap):
          weight = cost(cost_type, lat1 = lats[j,i], lon1 = lons[j,i], lat2 = lats[jm,ip], lon2 = lons[jm,ip], aice = aice[j,i])
          G.add_edge(n, nodemap[jm,ip], weight = weight)
  
  #debug: print("Have constructed graph, number of nodes, edges =",k, len(G.edges), flush=True)
  #debug: exit(0)

#--------------------------------------------------------------
# Now search for a path
  start  = nodemap[j_bering, i_bering]
  finish = nodemap[j_finish, i_finish]

  #debug: print(i_bering, j_bering, i_finish, j_finish, start, finish, nodemap[j_bering, i_bering], nodemap[j_finish, i_finish], flush=True)

  print(G.nodes[start])
  print(G.nodes[finish])
  
  print("Is there a path from start to finish? ",netx.has_path(G,start,finish ), flush=True )
  if (not netx.has_path(G,start,finish )):
    (i_finish, j_finish) = find(lons, lats, -126, 71.0)
    #(i_finish, j_finish) = find(lons, lats, -103, 74.35)
    #orig (i_finish, j_finish) = find(lons, lats, -78.0, 74.0)
    #exit(1)
    print("trying Bering strait to Banks island with ",i_finish, j_finish)
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

#---------- Output  ---------------------------------

  #---------- -- kml     ---------------------------------
  #debug: tag=datetime.datetime(2024,10,18)
  outname = "path_"+tag.strftime("%Y%m%d")+"_"+"{:03d}".format(hhh)+".kml"
  kmlout_path(outname, G, path)
  
  #---------- -- Graphics -----------------------------
  show(tlats, tlons, tag, hours=hhh, cost = pseudo_length, reference = 3686.) 
