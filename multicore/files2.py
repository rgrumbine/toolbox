import os
import sys
import datetime
import time

import multiprocessing as mp
import netCDF4 as nc

#def f(x,i):
def f(z):
    #print(x,os.getpid() )
    model = nc.Dataset(z[0])
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
      i = z[1]
      fout = open("file."+"{:d}".format(i),"wb")
      fout.write(icec)
      fout.close()
      print("wrote to fout ",os.getpid(), y )
      return y,icec

if __name__ == '__main__':

    print("cores available: ",mp.cpu_count() )

    # construct an iterable with the arguments -- plays nicer with pool.map
    x = []
    for i in range(1, len(sys.argv) ):
        x.append( [sys.argv[i], i] )

    with mp.Pool(processes=4) as pool:

        pool.map(f, x)

        pool.close()

    # exiting the 'with'-block has stopped the pool
    print("Now the pool is closed and no longer available")
