import os
import sys
import datetime
import time

import numpy as np
import multiprocessing as mp
import netCDF4 as nc

#ssmi:
def f(x,i):
#def f(x):
    #print(x,os.getpid() )
    model = nc.Dataset(x)
    y = len(model.dimensions['nobs'])
    lon  = model.variables['longitude'][:]
    lat  = model.variables['latitude'][:]
    icec = model.variables['ice_concentration'][:]
    qual  = model.variables['quality'][:]
    land  = model.variables['land_flag'][:]
    ymd   = model.variables['dtg_yyyymmdd'][:]
    hhmm  = model.variables['dtg_hhmm'][:]
    t19v  = model.variables['tb_19V'][:]
    t19h  = model.variables['tb_19H'][:]
    t22v  = model.variables['tb_22V'][:]
    t37v  = model.variables['tb_37V'][:]
    t37h  = model.variables['tb_37H'][:]
    #ssmi:
    #t85v  = model.variables['tb_85V'][:]
    #t85h  = model.variables['tb_85H'][:]
    #ssmi-s
    t92v  = model.variables['tb_92V'][:]
    t92h  = model.variables['tb_92H'][:]
    t150h = model.variables['tb_150H'][:]
    del(model)
    
    if (y == 0):
      print("y = 0", os.getpid(), flush=True)
      return y,0
    else:
      fout = open("file."+"{:d}".format(i),"wb")
      #for k in range(0,y)
      #  print(icec[k],file=fout, flush=True) # very slow
      #print(icec,file=fout, flush=True)
      fout.write(icec)
      fout.close()
      print("wrote to fout ",os.getpid(), y )
      return y,icec
    #return y

def g(y,icec,lat):
    return (y*lat.max() )

if __name__ == '__main__':

    #pool2 = mp.Pool(processes = 4)
    print("cores available: ",mp.cpu_count() )

    with mp.Pool(processes=3) as pool:

        #pool.map(f, sys.argv[1:])
        for i in range(1,len(sys.argv) ):
          res = pool.apply_async(f, (sys.argv[i],i) )      # runs in *only* one process
          # the following blocks until the result is available
          #y = res.get()
#          yy = y[0]
#          print(sys.argv[i], yy)
#          if (yy > 0):
#            res = pool2.apply_async(g, (yy,y[1],y[2]) )
#            print(sys.argv[i], yy, len(y[1]), y[1].max(), res.get() )

        #putting the get here gets more like expected results -- if close is also used
        res.get()
        print("For the moment, the pool remains available for more work")
        pool.close()

    # exiting the 'with'-block has stopped the pool
    print("Now the pool is closed and no longer available")
