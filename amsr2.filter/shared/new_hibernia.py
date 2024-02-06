import os
import sys
from math import *
import datetime
import numpy as np
import numpy.ma as ma

from filtering import *

from tools import *

def near_hibernia(tmp, fout = stdout) 
  if (near(tmp.obs.latitude,46.5,5.) and near(tmp.obs.longitude,-48.5, 5.) ):
    tmp.show(fout)
    #debug: tmp.show()

