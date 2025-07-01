import os
import sys

import numpy as np
import numpy.ma as ma

fin = open(sys.argv[1],"r")

try:
  title_tag = sys.argv[2]
except:
  title_tag = "ref"

try:
    markersize = float(sys.argv[3])
except:
    markersize = 1

lon = []
lat = []
cat = [] 

for line in fin:
  if ("c" in line):
    words = line.split()
    lon.append(float(words[22]))
    tll = float(words[21])
    lat.append(tll)
    cat.append(float(words[24]))

print(cat[33])
print("found ",len(lon)," points")
#debug print(max(lat), min(lat), max(lon), min(lon) )
latmax = max(lat)
latmin = min(lat)
lonmax = max(lon)
lonmin = min(lon)


# lat-lon plot of error points ---------------------------------
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg') #batch mode

import cartopy.crs as ccrs
import cartopy.feature as cfeature

#proj = ccrs.LambertConformal(central_longitude=-170., central_latitude = 60., cutoff=25.)
#proj = ccrs.PlateCarree()
proj = ccrs.SouthPolarStereo(central_longitude = -60)

ax = plt.axes(projection = proj)
#fig = plt.figure(figsize = (8,6))
fig = plt.figure()
ax = fig.add_subplot(1,1,1,projection = proj)
plt.title(title_tag)

xlocs = list(range(-180,181,30))
ylocs = list(range(-90, -35, 5))

ax.gridlines(crs=ccrs.PlateCarree(), xlocs=xlocs, ylocs=ylocs )
# not on hera: ax.coastlines()
ax.add_feature(cfeature.GSHHSFeature(levels=[1,2], scale="c") )

color = []
for i in range(0,10):
  color.append((i/10,i/10,i/10))
  tlat = []
  tlon = []
  for k in range(0,len(lon)):
    if (cat[k] == i):
      tlat.append(lat[k])
      tlon.append(lon[k])
  plt.scatter(tlon, tlat, transform=ccrs.PlateCarree(), s = markersize,  color = color[i])
  del tlat, tlon

plt.savefig("ll_errs_"+title_tag+".png")
plt.close()

print(markersize)
