import os
import sys

import numpy as np
import numpy.ma as ma

from graphics import *
#--------------------------------------------------------

first_chars = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '{' ]
def parse (line):
#RG: Handle blank lines and comment lines
    if (line[0] not in first_chars):
        #debug: print("illegal character starts line, skipping", flush=True)
        return(0,0,0,0)
    else:
      words = line.split()
      if (line[0] == '{'):
        try:
          i = int(words[1].split(',')[0])
          j = int(words[3].split(',')[0])
          lat = float(words[5].split(',')[0])
          lon = float(words[7].split(',')[0])
        except:
          print("problem with: \n",line, flush=True)
          return(0,0,0,0)
      else:
        i = int(words[0])
        j = int(words[1])
        lat = float(words[3])
        lon = float(words[2])
    return(i,j, lat, lon)

#--------------------------------------------------------

fin = open(sys.argv[1],"r")

#RG: extremely inelegant:
lons = np.zeros((1024*128))
lats = np.zeros((1024*128))

k=0
for line in fin:
    x = parse(line)
    #debug: print(x, x[0], x[1], flush=True)
    if (x[0] == 0 and x[1] == 0):
        continue
    lats[ k ] = x[2]
    lons[ k ] = x[3]

    k += 1

print('found',k,'pts')


#--------------------------------------------------------
print("about to call the graphic plotter",flush=True)

proj = ccrs.LambertConformal(central_longitude = -120,
           central_latitude = 75., cutoff = 45.)
#proj = ccrs.AzimuthalEquidistant(central_longitude = -120.,
#          central_latitude = 75.0)
#proj = ccrs.Orthographic(central_longitude = -120.,
#          central_latitude = 75.0)

ax, fig = show(proj, lats, lons, "hello" )
overlay(proj, ax, fig, lats[0:8000], lons[0:8000], color = 'green')

#--------------------------------------------------------
#Read in NIC's NWP and overlay it

import geopandas as gpd

fp = "NWP.shp"
data = gpd.read_file(fp)
orig = data

# Project on to my map style/CRS
anew = orig.to_crs(proj)
anew.plot(ax = ax, color = "blue")

ax.set_title("NIC NWP vs. ants")

plt.savefig("overlay.png")
plt.close()
