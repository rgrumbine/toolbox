import os
import sys

from math import *

import datetime

import numpy as np
import numpy.ma as ma

from filtering import *

# noodle satobs class and descendents
sat_lr = amsr2_lr()
tmp = match(sat_lr)

def near(x, y, delta):
    return(fabs(x-y) < delta)

#----------------------------------------------------------
fout = open(sys.argv[1], "a")

start = datetime.datetime(2022,1,1)
end   = datetime.datetime(2023,3,13)
#end   = datetime.datetime(2022,1,4)
dt = datetime.timedelta(1)

trips = 0
while (start <= end and trips < 3000):
  tag=start.strftime("%Y%m%d")
  filename = "amsr2."+tag+"/postperfect."+tag
  print(filename)
  count = 0
  if (os.path.exists(filename)):

    try:
        fin = open(filename, "r")
    except:
        print("failed to open input",filename)
        exit(1)

    for line in fin:
      tmp.read(line)
      #debug: print(tmp.obs.latitude, tmp.obs.longitude, flush=True)
    
      if (near(tmp.obs.latitude,46.5,5.) and near(tmp.obs.longitude,-48.5, 5.) ):
        tmp.show(fout)
        #debug: tmp.show()
        count += 1
    
    fin.close()

    print("found ", count, "hibernia points")
    #for i in range (0, len(lrmatch) ):
    #    lrmatch[i].show(fout)
    #    #debug: lrmatch[i].show()

  trips += 1
  start += dt

#---------------------------------------------------------------------
fout.close()

