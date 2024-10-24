import pygrib

#---------------------------------------------------------------
# Read ice analysis, add to matchup (icec)
tag8='20240101'
analy_base='/u/robert.grumbine/noscrub/sice/sice.'+tag8+'/'
fname=analy_base+'seaice.t00z.5min.grb.grib2'
grbs = pygrib.open(fname)
for x in grbs:
  #debug: print(x.shortName, x.name, x.level, x.typeOfLevel, x.paramId, x.forecastTime, flush=True)
  #debug: print(x, flush=True)
  #placeholder:
  print(x.values.max(), x.values.min(), flush=True )
icec = x.values

for i in range(0,len(allmatches)):
   allmatches[i].add_icec(icec)
   #debug:  if (i%1000 == 0):
   #debug:    allmatches[i].show()
del x, grbs

#debug: exit(0)
