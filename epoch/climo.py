'''
Harmonic climatology -- 
Robert Grumbine
'''
#import os
import sys
from math import pi, cos, sin, sqrt
import datetime
#import copy

import numpy as np
from numpy import ma
import netCDF4

#-------------------------------------------------
from functions import applymask
import ncoutput
from harmonic2 import harmonic_coeffs, harmonic_solve

# Define harmonic frequencies
loy = 365.2422 #days, tropical year

nfreq = 6
omega = np.zeros((nfreq))
omega[0] = 2.*pi/loy
omega[1] = 2.*pi/loy*2
omega[2] = 2.*pi/loy*3
omega[3] = 2.*pi/loy*4
omega[4] = 2.*pi/loy*5
omega[5] = 2.*pi/loy*6

#-------------------------------------------------
# location of data files
fbase = "/home/Robert.Grumbine/clim_data/replay/thinned/"

# Defining the grid
nx = 1536
ny = 768
dt = datetime.timedelta(1)

#epoch = datetime.datetime(1994,1,1)
#end = datetime.datetime(2023,12,31)

epoch = datetime.datetime(1994,1,1)
start = datetime.datetime(2007,1,1)
epoch = start
end = datetime.datetime(2024,12,31)
#end = datetime.datetime(1994,12,31)

prsparms = [ 'PRMSL_meansealevel', 'HGT_1mb', 'HGT_10mb', 'HGT_200mb', 'HGT_500mb', 'HGT_700mb', 'HGT_850mb' ]
#parm = 'HGT_10mb'
parm = sys.argv[1]
#-------------------------------------------------
# Initialize files for accumulations
sst = np.zeros((ny,nx)) # temporary file for reading in data
tmp = np.zeros((ny,nx))

# for accumulating moments:
sumx1 = np.zeros((ny,nx), dtype=np.float64)
sumx2 = np.zeros((ny,nx), dtype=np.float64)
sumx3 = np.zeros((ny,nx), dtype=np.float64)
sumx4 = np.zeros((ny,nx), dtype=np.float64)
#debug: print('dtype for sumx1 ',sumx1.dtype, flush=True)

# for trend
sumt  = np.zeros((ny,nx), dtype=np.float64)
sumxt = np.zeros((ny,nx), dtype=np.float64)
sumt2 = np.zeros((ny,nx), dtype=np.float64)

# for harmonic summing
hsum1    = np.zeros((ny, nx, nfreq), dtype=np.float64)
hsum2    = np.zeros((ny, nx, nfreq), dtype=np.float64)

# extrema
tmax = np.zeros((ny,nx))
tmin = np.zeros((ny,nx))
tmax.fill(-np.inf)
tmin.fill(+np.inf)

#---------------------------------------------
# Now run through the data files and accumulate terms:

tag = start
days = (tag - epoch).days
count = 0
n0   = days
while (tag <= end ):
    if (count % 30 == 0):
      print(tag, flush=True)

# Get the day's data:
    if (parm in prsparms):
      fname = "prs." + tag.strftime("%Y%m%d") + ".nc"
    else:
      fname = "flx." + tag.strftime("%Y%m%d") + ".nc"
    tmpnc = netCDF4.Dataset(fbase + fname)
    sst = tmpnc.variables[parm][0,:,:]
    if ( count ==  0 ):
        lons = tmpnc.variables['longitude'][:]
        lats = tmpnc.variables['latitude'][:]
    tmpnc.close()

# Accumulate moments:
    tmp = sst.copy()
    sumx1 += tmp
    tmp *= sst
    sumx2 += tmp
    tmp *= sst
    sumx3 += tmp
    tmp *= sst
    sumx4 += tmp

# Accumulate trend:
    tmp    = sst.copy()
    sumt  += float(days)
    sumt2 += float(days*days)
    sumxt += tmp*float(days)

# Accumulate harmonics:
    tmp = sst.copy()
    for j in range(0, nfreq):
      hsum1[:,:,j] += tmp * cos(omega[j]*days)
      hsum2[:,:,j] += tmp * sin(omega[j]*days)

# Find extrema:
    tmax = np.fmax(tmax, sst)
    tmin = np.fmin(tmin, sst)

    days  += 1   # days since epoch
    count += 1   # number of days' data
    tag   += dt

#------------------------------------------------
lda      = 2*nfreq
coeff    = np.zeros((lda, lda))
harmsums = np.zeros((ny, nx, nfreq*2))

harmonic_coeffs(coeff, omega, count, nfreq, n0 = n0) # rg: probably need n0 here, too.

mean = sumx1/count
#for j in range(0, nfreq):
#  harmsums[:,:,2*j  ]  = hsum1[:,:,j ]
#  harmsums[:,:,2*j+1]  = hsum2[:,:,j ]
#Gemini: Interleave cosine (even indices) and sine (odd indices) in two vectorized operations
harmsums[:, :, 0::2] = hsum1
harmsums[:, :, 1::2] = hsum2

# solve for harmonics-only
alpha    = np.zeros((ny, nx, nfreq))
beta     = np.zeros((ny, nx, nfreq))
harmonic_solve(coeff, harmsums, alpha, beta, nfreq)

#trend_harmonic_solve(coeff2, sumx1, sumxt, sumycos, sumysin,
#                      coeff, harmsums, alpha, beta, nfreq)

#------------------------------------------------
#RG: write out mean, max, min to save file
mask =  ma.masked_array(sumx1 < -900.*days)
indices = mask.nonzero()

applymask(sumx1, indices)
applymask(sumx2, indices)
applymask(sumx3, indices)
applymask(sumx4, indices)
applymask(sumxt, indices)
applymask(sumt, indices)
applymask(sumt2, indices)
applymask(alpha, indices)
applymask(beta , indices)

print("sumx1", sumx1.max(), sumx1.min() )
print("sumx2", sumx2.max(), sumx2.min() )
print("sumx3", sumx3.max(), sumx3.min() )
print("sumx4", sumx4.max(), sumx4.min() )
print("tmax", tmax.max() , tmax.min() )
print("tmin", tmin.max() , tmin.min() )
print("alpha", alpha.max(), alpha.min(), alpha.mean() )
print("beta ", beta.max(), beta.min(), beta.mean() )

ampls = np.zeros((ny, nx, nfreq))
phase = np.zeros((ny, nx, nfreq))

ampls = np.hypot(alpha, beta)
phase = np.degrees(np.arctan2(beta, alpha))
phase[phase < -180.] += 360.
phase[phase >  180.] -= 360.

#for j in range(0, nfreq):
#  #ampls[:,:,j] = np.sqrt(alpha[:,:,j]**2 + beta[:,:,j]**2)
#  #phase[:,:,j] = np.arctan2(beta[:,:,j], alpha[:,:,j])*180./pi
#  print(j, "ampls", ampls[:,:,j].max(), ampls[:,:,j].min(), ampls[:,:,j].mean() )
#  #debug: print(j, "phase", phase[:,:,j].max() )
#  for k in range(0,ny):
#    for l in range(0,nx):
#      if (phase[k,l,j] < -180.):
#        phase[k,l,j] += 360.
#      if (phase[k,l,j] >  180.):
#        phase[k,l,j] -= 360.

#-------------------------------------------------
name = f"epoch{start.year:4d}.nc"

foroutput = ncoutput.ncoutput(nx, ny, lats, lons, name)
foroutput.ncoutput(name)
foroutput.addvar('sumx1', dtype = sumx1.dtype)
foroutput.addvar('mean', dtype = sumx1.dtype)
foroutput.addvar('sumx2', dtype = sumx2.dtype)
foroutput.addvar('sumx3', dtype = sumx3.dtype)
foroutput.addvar('sumx4', dtype = sumx4.dtype)
foroutput.addvar('sumt', dtype = sumt.dtype)
foroutput.addvar('sumxt', dtype = sumxt.dtype)
foroutput.addvar('sumt2', dtype = sumt2.dtype)
foroutput.addvar('intercept', dtype = sumx1.dtype)
foroutput.addvar('slope', dtype = sumx1.dtype)
foroutput.addvar('correl', dtype = sumx1.dtype)
foroutput.addvar('tstat', dtype = sumx1.dtype)
foroutput.addvar('tmax', dtype = tmax.dtype)
foroutput.addvar('tmin', dtype = tmin.dtype)
foroutput.addvar('cpy1_amp', dtype = ampls.dtype)
foroutput.addvar('cpy1_pha', dtype = phase.dtype)
foroutput.addvar('cpy2_amp', dtype = ampls.dtype)
foroutput.addvar('cpy2_pha', dtype = phase.dtype)
foroutput.addvar('cpy3_amp', dtype = ampls.dtype)
foroutput.addvar('cpy3_pha', dtype = phase.dtype)
foroutput.addvar('cpy4_amp', dtype = ampls.dtype)
foroutput.addvar('cpy4_pha', dtype = phase.dtype)
foroutput.addvar('cpy5_amp', dtype = ampls.dtype)
foroutput.addvar('cpy5_pha', dtype = phase.dtype)
foroutput.addvar('cpy6_amp', dtype = ampls.dtype)
foroutput.addvar('cpy6_pha', dtype = phase.dtype)

mean = sumx1/count
applymask(mean, indices)
applymask(sumx1, indices)
applymask(sumxt, indices)
applymask(sumt, indices)
applymask(sumt2, indices)

tmpt = days*sumt2 - sumt*sumt
tmpx = days*sumx2 - sumx1*sumx1
print(tmpt.min(), tmpt.max(), tmpt.mean() )
tcount = 0
xcount = 0
tlim = tmpt.max()
xlim = tmpx.max()
mask_t = (tmpt == 0)
mask_x = (tmpx == 0)
tcount += np.count_nonzero(mask_t)
xcount += np.count_nonzero(mask_x)
tmpt[mask_t] = tmpt.max()
tmpx[mask_x] = tmpx.max()
#for j in range (0, ny):
#  for i in range (0, nx):
#    if (tmpt[j,i] == 0):
#      tmpt[j,i] = tlim
#      tcount += 1
#    if (tmpx[j,i] == 0):
#      tmpx[j,i] = xlim
#      xcount += 1
print("count of zero tmpt",tcount, "tmpx",xcount)
print(tmpt.min(), tmpt.max(), tmpt.mean() )

slope = (days*sumxt - sumx1*sumt) / tmpt #RG: should be from trend solver
applymask(slope, indices)

intercept = sumx1/days - slope*sumt/days #RG: ditto
applymask(intercept, indices)

correl = (days*sumxt - sumx1*sumt ) / (np.sqrt(tmpt) * np.sqrt(tmpx))
applymask(correl, indices)

tstat = correl*sqrt(days) / (1. - correl*correl)
applymask(tstat, indices)

foroutput.encodevar(sumx1, 'sumx1')
foroutput.encodevar(mean,  'mean')
foroutput.encodevar(sumx2, 'sumx2')
foroutput.encodevar(sumx3, 'sumx3')
foroutput.encodevar(sumx4, 'sumx4')
foroutput.encodevar(sumt,  'sumt')
foroutput.encodevar(sumxt, 'sumxt')
foroutput.encodevar(sumt2, 'sumt2')
foroutput.encodevar(slope, 'slope')
foroutput.encodevar(intercept, 'intercept')
foroutput.encodevar(correl, 'correl')
foroutput.encodevar(tstat,  'tstat')
foroutput.encodevar(tmin,   'tmin')
foroutput.encodevar(tmax,   'tmax')
foroutput.encodevar(ampls[:,:,0], 'cpy1_amp')
foroutput.encodevar(phase[:,:,0], 'cpy1_pha')
foroutput.encodevar(ampls[:,:,1], 'cpy2_amp')
foroutput.encodevar(phase[:,:,1], 'cpy2_pha')
foroutput.encodevar(ampls[:,:,2], 'cpy3_amp')
foroutput.encodevar(phase[:,:,2], 'cpy3_pha')
foroutput.encodevar(ampls[:,:,3], 'cpy4_amp')
foroutput.encodevar(phase[:,:,3], 'cpy4_pha')
foroutput.encodevar(ampls[:,:,4], 'cpy5_amp')
foroutput.encodevar(phase[:,:,4], 'cpy5_pha')
foroutput.encodevar(ampls[:,:,5], 'cpy6_amp')
foroutput.encodevar(phase[:,:,5], 'cpy6_pha')

tmask = np.zeros((ny,nx))
tmask[indices[0], indices[1]] = 1.0
#for k in range(0, len(indices[0]) ):
#    i = indices[1][k]
#    j = indices[0][k]
#    tmask[j,i] = 1.0
foroutput.addvar('mask', dtype = tmask.dtype)
foroutput.encodevar(tmask, 'mask')

print("number of days = ",count)
foroutput.encodescalar(days, 'days')

foroutput.close()
#------------------ End of first pass --------------------------
