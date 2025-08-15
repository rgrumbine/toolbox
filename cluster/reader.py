import sys
import numpy as np
import pygrib
import netCDF4
import datetime


"""
read:
 open posteriori file
   read in to llgrid, 1/12th

 open sst file for day
   read in (grib manage lat-lon?)
 open A file for day
   read in (grib manage lat-lon?)
 scan tb file for day
  if lr in line:
    write back out with posteriori flag, sst, A

"""
#-----------------------------------------------------------------------

def read(tag, ary, dr, count, countmax = int(14123456), fmax = int(2123456), thin = 100 ):

  base='/export/emc-lw-rgrumbi/rmg3/obs/'
  fcount = 0
  tcount = 0
  #debug: print(tag, count, flush=True)
  ymd = tag.strftime("%Y%m%d") 
  fname = base+"seaice_analysis."+ymd+"/amsr2_"+ymd+".txt.1"
  fin = open(fname,"r")

  post = netCDF4.Dataset(base+"posteriori.nc")
  flag = post.variables['posteriori'][:,:]

  sst = pygrib.open(base+"nsst/"+ymd+"/rtgssthr_grb_0.083.grib2")
  conc = pygrib.open(base+"analy/seaice_analysis."+ymd+"/seaice.t00z.5min.grb.grib2")
  svals = sst[1].values
  avals = conc[1].values

  for line in fin:
    if ('lr' in line):
      tcount += 1
      if ((tcount % thin) != 0):
        #debug: print("thinning",tcount)
        continue
      words = line.split()
      tlat = float(words[1])
      tlon = float(words[2])
      # find ti, tj for posteriori (and sst, conc) grid
      tj = int(np.rint(0.5+(tlat - 90 + 1./24.)/(-1./12.)))
      ti = int(np.rint(0.5+(tlon -      1./24.)/(1./12.)))
  
      ## skip areas that are always warm
      #if (flag[tj, ti] <= 164):
      #  continue
      ## Skip points that would be filtered by sst
      if (svals[tj,ti] > 275.3):
          continue
  
      for k in range(0,12):
        ary[count,k] = float(words[k+3])
      ary[count,12] = flag[tj, ti]
      ary[count,13] = svals[tj, ti]
      ary[count,14] = avals[tj, ti]
      ary[count,15] = tlat
      ary[count,16] = tlon
  
      pcount = 0
      for l in range(0,12):
        for m in range(l+1,12):
          dr[count,pcount] = (ary[count,l] - ary[count,m])/(ary[count,l]+ary[count,m])
          pcount += 1
      for l in range(0,12):
        dr[count,l+pcount] = ary[count,l]
  
  
      fcount += 1
      count  += 1
  
    if (fcount >= fmax):
      print('reached fmax of ',fmax, tcount, flush=True)
      fin.close()
      break
    if (count >= countmax):
      print('reached countmax of ',countmax, flush=True)
      break

  #debug: print(fcount,"read from file")
  fin.close()

  count = min(count, countmax)
  #debug: print(count, " points to consider v countmax",countmax, flush=True)
  return count
#-----------------------------------------------------------------------

# compute (x1^2-x2^2)/(x1^2+x1^2) rather than bilinear dr
def read2(tag, ary, dr, count, countmax = int(14123456), fmax = int(2123456) ):
  base='/export/emc-lw-rgrumbi/rmg3/obs/seaice_analysis.'
  post = netCDF4.Dataset("posteriori.nc")
  flag = post.variables['posteriori'][:,:]

  fcount = 0
  #debug: print(tag, flush=True)
  ymd = tag.strftime("%Y%m%d") 
  fname = base+"seaice_analysis."+ymd+"/amsr2_"+ymd+".txt.1"
  fin = open(fname,"r")
  sst = pygrib.open(base+"nsst/"+ymd+"/rtgssthr_grb_0.083.grib2")
  conc = pygrib.open(base+"analy/seaice_analysis."+ymd+"/seaice.t00z.5min.grb.grib2")

  svals = sst[1].values
  avals = conc[1].values

  for line in fin:
    if ('lr' in line):
      words = line.split()
      tlat = float(words[1])
      tlon = float(words[2])
      # find ti, tj for posteriori (and sst, conc) grid
      tj = int(np.rint(0.5+(tlat - 90 + 1./24.)/(-1./12.)))
      ti = int(np.rint(0.5+(tlon -      1./24.)/(1./12.)))
  
      if (svals[tj,ti] > 275.3):
          continue
  
      for k in range(0,12):
        ary[count,k] = float(words[k+3])
      ary[count,12] = flag[tj, ti]
      ary[count,13] = svals[tj, ti]
      ary[count,14] = avals[tj, ti]
      ary[count,15] = tlat
      ary[count,16] = tlon
  
      pcount = 0
      for l in range(0,12):
        for m in range(l+1,12):
          dr[count,pcount] = (ary[count,l]**2 - ary[count,m]**2)/(ary[count,l]**2+ary[count,m]**2)
          pcount += 1
      for l in range(0,12):
        dr[count,l+pcount] = ary[count,l]
  
  
      fcount += 1
      count  += 1
  
    if (fcount >= fmax):
      print('reached fmax of ',fmax, flush=True)
      fin.close()
      break
    if (count >= countmax):
      print('reached countmax of ',countmax, flush=True)
      break

  #debug: print(fcount,"read from file")
  fin.close()

  count = min(count, countmax)
  #debug: print(count, " points to consider v countmax",countmax, flush=True)
  return count
#---------------------------------------------------------
'''
reread works from a prior run which already spliced in the flags, sst, icec
it needs the file name input, not date
'''
def reread(fname, ary, dr, count, countmax = int(14123456), fmax = int(2123456) ):
  fcount = 0
  fin = open(fname,"r")

  for line in fin:
      words = line.split()
  
      for k in range(0,17):
        ary[count,k] = float(words[k])
  
      pcount = 0
      for l in range(0,12):
        for m in range(l+1,12):
          dr[count,pcount] = (ary[count,l] - ary[count,m])/(ary[count,l]+ary[count,m])
          pcount += 1
      for l in range(0,12):
        dr[count,l+pcount] = ary[count,l]
  
      fcount += 1
      count  += 1
  
      if (fcount >= fmax):
        print('reached fmax of ',fmax, flush=True)
        fin.close()
        break
      if (count >= countmax):
        print('reached countmax of ',countmax, flush=True)
        break

  #debug: print(fcount,"read from file")
  fin.close()

  count = min(count, countmax)
  #debug: print(count, " points to consider v countmax",countmax, flush=True)
  return count
#---------------------------------------------------------
