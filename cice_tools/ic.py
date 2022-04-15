import os
import sys

import numpy as np
import netCDF4 as nc

f1 = sys.argv[1]

d1 = nc.Dataset(f1, "r")

#variables:
parms2 = [ "uvel", "vvel", "stressp_1", "stressp_2", "stressp_3", "stressp_4", "stressm_1", "stressm_2", "stressm_3", "stressm_4", "stress12_1", "stress12_2", "stress12_3", "stress12_4", "scale_factor", "swvdr", "swvdf", "swidr", "swidf", "strocnxT", "strocnyT", "iceumask", "sst", "frzmlt", "frz_onset", "fsnow" ]

for parms in parms2:
    p1 = d1.variables[parms][:,:]
    print(parms, p1.max(), p1.min() )
    
ncat = 5
ni = 384
nj = 320
sums = np.zeros((nj, ni))

print("\n")
parms3 = [ "aicen", "vicen", "vsnon", "Tsfcn", "iage", "FY", "alvl", "vlvl", "apnd", "hpnd", "ipnd", "dhs", "ffrac", "fbrn", "first_ice", "sice001", "qice001", "sice002", "qice002", "sice003", "qice003", "sice004", "qice004", "sice005", "qice005", "sice006", "qice006", "sice007", "qice007", "qsno001" ]
for parms in parms3:
    sums = 0.0
    p3 = d1.variables[parms][:,:,:]
    for i in range(0,ncat):
        print(" ",i,p3[i,:,:].max(), p3[i,:,:].min() )
        sums += p3[i,:,:]
    print(parms,sums.max(), sums.min() )

