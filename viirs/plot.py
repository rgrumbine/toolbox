import os
import sys

import numpy as np

fin = open(sys.argv[1],"r")

try:
  title_tag = sys.argv[2]
except:
  title_tag = "ref"

markersize = float(sys.argv[3])

parm = []
i = []
j = []
lon = []
lat = []

for line in fin:
  if ("grid" in line):
    words = line.split()
    i.append(int(words[1]))
    j.append(int(words[2]))
    lat.append(float(words[3]))
    lon.append(float(words[4]))

print("found ",len(i)," points")
if (len(i) == 0):
    exit(0)

#debug print(max(lat), min(lat), max(lon), min(lon) )
latmax = max(lat)
latmin = min(lat)
lonmax = max(lon)
lonmin = min(lon)


# i-j plot of points ----------------------------------
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg') #batch mode

#Elaborations:
#  title
#  axis labels
#  separate color/symbol per parameter
#  different sizes per parameter

fig,ax = plt.subplots()
plt.scatter(i,j, s = markersize)
ax.grid() 
plt.title(title_tag)
plt.savefig("ij_"+title_tag+".png")
plt.close()


# lat-lon plot of error points ---------------------------------
import cartopy.crs as ccrs
import cartopy.feature as cfeature

#proj = ccrs.LambertConformal(central_longitude=-170., central_latitude = 60., cutoff=25.)
proj = ccrs.PlateCarree()
proj = ccrs.SouthPolarStereo(central_longitude=-60)
proj = ccrs.NorthPolarStereo(central_longitude=-80)
proj = ccrs.NorthPolarStereo(central_longitude=-170)

ax = plt.axes(projection = proj)
fig = plt.figure(figsize = (8,6))
ax = fig.add_subplot(1,1,1,projection = proj)
plt.title(title_tag)

# AA
#xlocs = list(range(-180,181,30))
#ylocs = list(range(-90, -30, 5))
#ax.set_extent([-180,180,-90,-30], crs=ccrs.PlateCarree())
# Arctic
xlocs = list(range(-180,181,30))
ylocs = list(range(30,90,5))
ax.set_extent([-180,180,35,90], crs=ccrs.PlateCarree())
#Bering sea-ish
#ax.set_extent([-180,-90,35,90], crs=ccrs.PlateCarree())

ax.gridlines(crs=ccrs.PlateCarree(), xlocs=xlocs, ylocs=ylocs )
# not on hera: ax.coastlines()
ax.add_feature(cfeature.GSHHSFeature(levels=[1,2], scale="c") )
if markersize < 12:
    alpha = 1
else:
    alpha = 0.2/25

plt.scatter(lon, lat, transform=ccrs.PlateCarree(), s = markersize, alpha = alpha)
plt.savefig("ll_"+title_tag+".png")
plt.close()

#debug: print(markersize)
