import numpy as np
from math import *

import networkx as netx
import netCDF4
from netCDF4 import Dataset

ratio = 1
ny = int(20*ratio)
nx = int(2*ny)
nodemap = np.zeros((ny, nx),dtype="int")

k = int(1)
G = netx.Graph()
for i in range(0,nx):
  for j in range(0,ny):
      nodemap[j,i] = int(k)
      G.add_node(int(k), i=i, j=j)
      k += int(1)
print("Done adding nodes, k=",k, flush=True)

dweight = 1.4
ibear =  5
jbear =  7
for j in range(1,ny-1):
  i = 0
  jp = j + 1
  jm = j - 1
  for i in range(1,nx-1):
    n = nodemap[j,i]
    ip = i+1
    im = i-1
    #w = 1.0  # unweighted
    #w = sqrt((i-ibear)**2 + (j-jbear)**2) # Like the bear
    w = exp(-((i-ibear)**2 + (j-jbear)**2) / 2. /0.5**2 )  #Avoid the bear
    if (i >= 0 and jm >= 0 and jp < ny):
      G.add_edge(n, nodemap[jp,i], weight=w)
      G.add_edge(n, nodemap[jm,i], weight=w)
    if (j >= 0 and im >= 0 and ip < ny):
      G.add_edge(n, nodemap[j,im], weight=w)
      G.add_edge(n, nodemap[j,ip], weight=w)
    if (i >= 0 and jm >= 0 and jp < ny and j >= 0 and im >= 0 and ip < ny):
      G.add_edge(n, nodemap[jm,im], weight=w*dweight)
      G.add_edge(n, nodemap[jm,ip], weight=w*dweight)
      G.add_edge(n, nodemap[jp,im], weight=w*dweight)
      G.add_edge(n, nodemap[jp,ip], weight=w*dweight)
print("Have constructed graph", flush=True)

i_bering = 1
j_bering = 1
i_finish = 9*ratio
j_finish = 15*ratio

print("start, finish i,j:",i_bering, j_bering, i_finish, j_finish)
start  = nodemap[j_bering, i_bering]
finish = nodemap[j_finish, i_finish]

print("start, finish node #",start, finish)
print("start node:",G.nodes[start])
print("finish node:",G.nodes[finish])
print("Is there a path from start to finish? ",netx.has_path(G,start,finish ), flush=True )

if (not netx.has_path(G,start,finish )):
  exit(1)

path = netx.dijkstra_path(G,start, finish, weight='weight')
print("dijkstra length ", len(path), flush=True)

#exit(0)
for k in range(0,len(path)):
  print(k, path[k], G.nodes[path[k]],
        flush=True )
