import os
import sys
import datetime
import time

import numpy as np
import multiprocessing as mp

def f(x,i):
    x[i] *= -i
    x[i] = os.getpid()
    #print(len(x), x[i], os.getpid() )
    #print(x[i], os.getpid() )
    return x

if __name__ == '__main__':

    x = np.linspace(0,32,33)

    with mp.Pool(processes=4) as pool:

        for i in range(0,len(x) ):
          res = pool.apply_async(f, (x,i) )      # runs in *only* one process
          x = res.get()
          print(i,x[i])

        try:
            print(res.get(timeout=1))
        except mp.TimeoutError:
            print("We lacked patience and got a multiprocessing.TimeoutError")

        print("For the moment, the pool remains available for more work")

    # exiting the 'with'-block has stopped the pool
    print("Now the pool is closed and no longer available")
    print(x)
