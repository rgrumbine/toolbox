#!/u/robert.grumbine/env3.10/bin/python3
# python system
import os
import sys
from math import *
import datetime

# env libraries
import numpy as np
import numpy.ma as ma

# shared
import match
from filtering import *
from tools import *

#---------------------------------------------------------------
#                     Data Acquisition
# Read in the satellite obs to matchup -- satobs class in match file
# 
#tb_lr = np.zeros((amsr2_lr.ntb))
#tb_hr = np.zeros((amsr2_hr.ntb))
#sat_lr = amsr2_lr()
#tmp = match(sat_lr)
tb_lr = np.zeros((match.amsr2_lr.ntb))
tb_hr = np.zeros((match.amsr2_hr.ntb))
sat_lr = match.amsr2_lr()
tmp = match.amsr2_lr()

# Read in the ice fixed file (for distance to land, posteriori filter, ..)
# ice_distance, ice_land, ice_post, ice_latitude, ice_longitude
# Needs seaice_fixed_fields.nc in cwd
from icefix import *
#debug: print(ice_post.max(), flush=True)

# Add ice fixed info to matchup (ice_land, ice_post, ice_distance)

# Read ice analysis, add to matchup (icec)

# Read sst analysis, add sst and analysis' ice conc to match (sst, ice_sst)

#---------------------------------------------------------------
