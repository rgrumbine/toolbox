import os
import datetime

#-----------------------------------------------------------------===
#    getting the forecast files

def fcst_name(valid, initial, fcst_dir):
#n.b.: assumes that valid and initial are same type
  #debug print("fcst_name values: valid, initial, fcstdir:",valid, initial,fcst_dir, flush=True)
  #debug print("types valid, initial, fcstdir: ",type(valid), type(initial), type(fcst_dir), flush=True )

  tvalid = tostr(valid)
  tinitial = tostr(initial)
  #debug: print(tvalid, tinitial, type(tvalid), type(tinitial) , flush=True )

  #Some UFS prototype name formats:
  #fname = fcst_dir + '/ice' + tvalid + '00.01.' + tinitial + '00.nc'
  #fname = fcst_dir + '/ice' + tvalid +   '.01.' + tinitial + '00.nc'
  #fname = fcst_dir + '/ice' + tvalid +   '.01.' + tinitial + '00.subset.nc'
  #fname = fcst_dir + '/ice' + tvalid +   '.01.' + tinitial + '00.subset.nc'

  fname = fcst_dir + '/ice' + tvalid +   '.01.' + tinitial + '00.subset.nc'

  #CICE consortium default
  #fdate = parse_8digits(int(tvalid))
  #fname = fcst_dir+'iceh.'+fdate.strftime("%Y")+'-'+fdate.strftime("%m")+'-'+fdate.strftime("%d")+".nc"

  #debug: print("\nfname, type\n", fname, type(fname),flush=True)
  if (not os.path.exists(fname) ):
    print("fcst_name: verf_files.py could not find forecast for "+
              fcst_dir, str(valid), str(initial), flush=True)
    print(fname, flush=True)
    #intolerant: 
    exit(1)
    #return 1
  else:
    return fname

def get_fcst(initial_date, valid_date, fcst_dir):
  retcode = int(0)
  initial = int(initial_date.strftime("%Y%m%d"))
  valid   = int(valid_date.strftime("%Y%m%d"))
  #debug print('get fcst ',initial, valid, flush=True)
  #debug print('get fcst ', initial, type(initial), initial_date, type(initial_date))

  #debug: print("get_fcst calling fcst_name", flush=True)
  fname = fcst_name(valid, initial, fcst_dir)
  #debug print("fname = ",fname, flush=True)

  if (not os.path.exists(fname)):
    retcode += 1
    print("Do not have forecast file ",fname," for ",initial, valid, flush=True)
  return retcode


#pass 8digit dates:
def fcst_edge(initial, valid, fcst_dir, fixdir, exdir):
  retcode = int(0)
  edgedir = dirs['edgedir']
  fname = edgedir + 'fcst_edge.' + str(valid)
  #debug: print("edgedir, fname ",edgedir, fname, flush=True)
 
  #if (not os.path.exists(fname) ):
  if (os.path.exists(fname) ):
    print("already have ",fname," skipping", flush=True)

  else:
    #debug: print("fcst_edge calling fcst_name", flush=True)

    fcstin = fcst_name(valid, initial, fcst_dir)
    if (type(fcstin) == int):
      print("verf_files.py fcst_edge Could not find forecast for ",valid, initial, fcst_dir)
      return 1
    #RG: want something cleaner for selecting model format/version!
    #UFS
    #debug: print("cmd", type(exdir), type(fixdir), type(fcstin), type(valid), flush=True )
    cmd = exdir + 'find_edge_cice '+fixdir+'skip_hr ' + fcstin + ' 0.40 > ' + fname

    #CICE
    #cmd = exdir + 'find_edge_consortium '+fixdir+'skip_hr ' + fname + ' 0.40 > fcst_edge.' + str(valid)

    x = os.system(cmd)
    if (x != 0): retcode += x
  return retcode

#------------------------------------------------------------------
