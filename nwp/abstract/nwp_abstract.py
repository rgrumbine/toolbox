'''
abc = abstract base class 
demo
'''
from abc import ABC, abstractmethod

class pathfinder(ABC):
    #llbox (NWP, NEP, NSR)
    #start, finish points (NWP, NEP, NSR)

    @abstractmethod
    # base = path to directory, tag = date -- user customizes for their model
    def file_name(base, tag): 
        pass

    @abstractmethod
    # pass a netcdf file to user function to derive the mask, return a grid + indices
    def getmask(ncfile):  
        pass

    @abstractmethod
    # Given a Graph's nodes, lons, lats, nodemap, and cost_type, connect the edges
    # Needs to be user-defined because with, e.g., tripolar grids adjacency in 
    #    i,j is not necessarily adjacent in lat-lon
    def edges(G, lons, lats, nodemap, offmap, aice, cost_type ):
        pass

# Move this to 'functions' -- it is general
    def make_nodes(lats, lons, llbox, land):
      offmap = 0
      nodemap = np.full((ny,nx),int(offmap), dtype="int")

      #Not a directed graph
      G = netx.Graph()

      k = int(1)
      for i in range(0,nx):
        for j in range(0,ny):
          # change to nwp.inbox(lon, lat)
          if (lats[j,i] > llbox.latmin and lats[j,i] < llbox.latmax and
              lons[j,i] > llbox.lonmin and lons[j,i] < llbox.lonmax     ):
            if (land[j,i] == 0):
              nodemap[j,i] = int(k)
              #n.b.: It is necessary to include explicit cast or the printing
              #        lists np.float32(value) rather than value
              G.add_node(k, i = i, j =j, lat = float(lats[j,i]),
                         lon = float(lons[j,i]),  aice= float(aice[j,i]),
                         hi = float(hi[j,i]) )
              k += int(1)
      #debug: print("Done adding nodes, k=",k, flush=True)
      return (G, nodemap)


