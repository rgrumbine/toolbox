import os
import sys
import datetime
import time

import numpy as np
import multiprocessing as mp

def f(x,i):
    #x[i] *= -1
    #print(len(x), x[i], os.getpid() )
    x *= -i
    #print(x, i, os.getpid() )
    return x

if __name__ == '__main__':

    x = np.linspace(0,32,33)
    #x = [1,2,3,4,5,6]
    #print(x, len(x), x[2])

    with mp.Pool(processes=4) as pool:

        for i in range(1,len(x) ):
          res = pool.apply_async(f, (x[i],i,) )      # runs in *only* one process
          x[i] = res.get()
          print(i,x[i])

        try:
            print(res.get(timeout=1))
        except mp.TimeoutError:
            print("We lacked patience and got a multiprocessing.TimeoutError")

        print("For the moment, the pool remains available for more work")

    # exiting the 'with'-block has stopped the pool
    print("Now the pool is closed and no longer available")
    print(x)
