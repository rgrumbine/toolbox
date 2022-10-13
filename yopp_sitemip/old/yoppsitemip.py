import os  
import sys 

import csv 

# Parse a string to a value, later to add a
def llparse(x, standard="null"):
  # start with labelled string
  if (x[-1] == 'N' or x[-1] == 'E'):
    tmp = float(x[0:-1])
  elif (x[-1] == 'S' or x[-1] == 'W'):
    tmp = -float(x[0:-1])
  # else assume it's a clean number
  else:
    tmp = float(x)
#RG: Would be a good idea to have the option of enforcing some longitude standards
  return tmp

#Define standards by the minimum allowed longitude, -360, -180, 0
def lon_standards(x, lonmin = -999., lonmax = 999.):
  tmp = x  
  if (tmp < lonmin):  
    while(tmp < lonmin):
      tmp += 360.
  if (tmp > lonmax): 
    while (tmp > lonmax):
      tmp -= 360.
  return tmp


delta = 0.25
idelta = 1./delta

x = -360.0*5.-120.
print(x, lon_standards(x,lonmin = -180.) )
print(x, lon_standards(x,lonmin = 0.) )
exit(0)

with open(sys.argv[1],'r') as fn:
  sreader = csv.reader(fn, delimiter=',')
  k = 0
  for line in sreader:
    name = str.strip(line[0])
    slat = line[1]
    slon = line[2]
    lat  = llparse(slat)
    lon  = llparse(slon)
    flat = max(-90.,float( int(lat*idelta+0.5)*delta - 1.0))
    flon = float( int(lon*idelta+0.5)*delta - 1.0)
    print("wgrib2 $fin -append -ncpu 1 -lola",
          "{:6.2f}".format(flat)+":10:0.25",
          "{:7.2f}".format(flon)+":10:0.25",
          name+".$type grib > /dev/null")

    k += 1

