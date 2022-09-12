import pygrib

#RG library (also wants ijpt, latpt, const)
from grid import *

from utility import *

#open for reading:
grbs = pygrib.open("gfs.t00z.sfluxgrbf000.grib2")
print("grbs = ",grbs)

get_ll_info(grbs)
    
grbs.seek(0)
k = 1
for grb in grbs:
  x = grb.values

  y = x[5:15,3:13]
  print("y = ",y)

  k += 1

print("k = ",k)
