import os
import sys

import numpy as np
import netCDF4 as nc

f1 = sys.argv[1]
f2 = sys.argv[2]

d1 = nc.Dataset(f1, "r")
d2 = nc.Dataset(f2, "r")


ni = 320 
nj = 384 
lats = d1.variables["TLAT"][:,:]
lons = d1.variables["TLON"][:,:]
tmask1 = d1.variables["tmask"][:,:]
tmask2 = d2.variables["tmask"][:,:]
tarea1 = d1.variables["tarea"][:,:]
tarea2 = d2.variables["tarea"][:,:]
aice1  = d1.variables["aice"][:,:]
aice2  = d2.variables["aice"][:,:]
print("aice1 ",aice1.max(), aice1.min() )
print("aice2 ",aice2.max(), aice2.min() )
aice1 -= aice2
print("delta ",aice1.max(), aice1.min() )

for parms in ("hi", "Tsfc", "uvel", "vvel"):
    p1 = d1.variables[parms][:,:]
    p2 = d2.variables[parms][:,:]
    print(parms, " 1 ", p1.max(), p1.min() )
    print(parms, " 2 ", p2.max(), p2.min() )
    p1 -= p2
    print(parms, " delta ", p1.max(), p1.min() )
    
