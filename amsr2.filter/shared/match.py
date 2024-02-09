import sys
import copy
import numpy as np


"""
Multiline comment.

Matchup class is aimed at matching satellite observations (class satobs) 
  against ice/ocean/geographic information.

For the satellite side, each satellite has:
    an identification
    a location for the observation
    ntb brightness channel observations

"""
 
"""
class satobs
    has ntb of brightness temperatures
    satellite identifier
    observation latitude, longitude, date
"""
class satobs:
  def __init__(self, ntb = 0, satid = 0, latitude = 95., longitude = -900., land = -1):
        self.ntb       = ntb
        self.satid     = satid
        self.latitude  = latitude
        self.longitude = longitude
        self.land      = land
        self.tb        = np.zeros((ntb))

  def add_tb(self, tb):
    for i in range (0,self.ntb):
      self.tb[i] = tb[i]

  def __getitem__(self, i):
    return(self.tb[i])

  def show(self, fout = sys.stdout ):
    print(self.satid, "{:10.5f}".format(self.longitude), "{:9.5f}".format(self.latitude),
    end="",file = fout)
    for i in range(0,self.ntb):
      print(" {:6.2f}".format(self.tb[i]),end="", file=fout)
    print(" ",end="", file=fout)

  def read(self, line):
  #read from a text line, assuming that the satobs is the first set of things on the line
    words = line.split()
    # Older:
    #self.satid  = int(words[0])
    #self.longitude = float(words[1])
    #self.latitude = float(words[2])
    #for i in range(0,self.ntb):
    #  self.tb[i] = float(words[3+i])
    #Current:
    self.satid  = 0
    self.latitude = float(words[1])
    self.longitude = float(words[2])
    i = words[3]
    j = words[4]
    self.land = 1.-float(words[5])
    for i in range(0,self.ntb):
      self.tb[i] = float(words[6+i])

class amsr2_lr(satobs):
  ntb = 12
  freq = np.zeros((ntb))
  freq[0] = 6.9
  freq[1] = 6.9
  freq[2] = 7.3
  freq[3] = 7.3
  freq[4] = 11.
  freq[5] = 11.
  freq[6] = 19.
  freq[7] = 19.
  freq[8] = 24.
  freq[9] = 24.
  freq[10] = 37.
  freq[11] = 37.

  def __init__(self, satid = 0, latitude = 95., longitude = -900.):
        self.satid     = satid
        self.latitude  = latitude
        self.longitude = longitude
        self.tb        = np.zeros((self.ntb))

class amsr2_hr(satobs):
  ntb = 2
  #RG: def freq

  def __init__(self, satid = 0, latitude = 95., longitude = -900.):
        self.satid     = satid
        self.latitude  = latitude
        self.longitude = longitude
        self.tb        = np.zeros((self.ntb))

class avhrr(satobs):
  ntb = 7
  #RG: def wavelength
  def __init__(self, satid = 0, latitude = 95., longitude = -900.):
        self.satid     = satid
        self.latitude  = latitude
        self.longitude = longitude
        self.tb        = np.zeros((self.ntb))

class viirs(satobs):
  ntb = 7
  #RG: def wavelength
  def __init__(self, satid = 0, latitude = 95., longitude = -900.):
        self.satid     = satid
        self.latitude  = latitude
        self.longitude = longitude
        self.tb        = np.zeros((self.ntb))

class ssmis(satobs):
  ntb = 7
  #RG: def freq
  def __init__(self, satid = 0, latitude = 95., longitude = -900.):
        self.satid     = satid
        self.latitude  = latitude
        self.longitude = longitude
        self.tb        = np.zeros((self.ntb))

#---------------------------------------------------------------------

# satellite to ice/ocean matchup class
#matchup :
#longitude, latitude, quality, land, icec;
#    ice_land, ice_post, ice_distance; sst, ice_sst, ims

from tools import *
class match:

  def __init__(self, sat = 0., icec = 95., land = 95, quality = 95, ice_land = 95, ice_post = 95, ice_distance = 95., sst = 95., ice_sst = 95., ims = [8,8,8,8,8] ):
      #RG: insinstance(sat_obs)
    self.obs = sat
    self.land = land

    self.icec = icec
    self.ims  = ims

    self.ice_land = ice_land
    self.ice_post = ice_post
    self.ice_distance = ice_distance

    self.sst     = sst
    self.ice_sst = ice_sst

    self.quality  = quality

  def show(self, fout = sys.stdout):
    #self.obs.show(fout)
    print(self.obs.satid, "{:10.5f}".format(self.obs.longitude), "{:9.5f}".format(self.obs.latitude),
    end="",file = fout)
    for i in range(0,self.obs.ntb):
      print(" {:6.2f}".format(self.obs.tb[i]),end="", file=fout)
    print(" ",end="", file=fout)
    # rest of matchup
    print("{:.2f}".format(self.icec), "{:.2f}".format(self.land), self.quality,
          "{:3d}".format(self.ice_land), "{:3d}".format(self.ice_post),
                   "{:7.2f}".format(self.ice_distance),
          "  ", "{:.2f}".format(self.sst), "{:.2f}".format(self.ice_sst),
          "  ",self.ims, end="",file = fout) 
    print("",file=fout)

  def hello(self):
      print("hello",flush=True)

  def lr_read(self, line):
    self.obs.read(line)
    base= 3 + self.obs.ntb
    words = line.split()
    self.icec     = float(words[base + 0])
    self.land     = float(words[base + 1])
    self.quality  = float(words[base + 2])
    self.ice_land = int(words[base + 3])
    self.ice_post = int(words[base + 4])
    self.ice_distance = float(words[base + 5])
    self.sst          = float(words[base + 6])
    self.ice_sst      = float(words[base + 7])
    #debug: print("lr_read: ",end="", flush=True)
    #debug  self.show()

  def add_oiv2(self, sst, ice_sst):
    j,i          = oiv2(self.obs.latitude, self.obs.longitude)
    self.sst     = sst[j,i]
    self.ice_sst = ice_sst[j,i]

  def add_icec(self, icec):
    #debug: print("icec max min",icec.max(), icec.min() )
    j,i = rg12th(self.obs.latitude, self.obs.longitude)
    #debug: print("j,i lat lon = ",j,i,self.obs.latitude, self.obs.longitude,flush=True)
    self.icec = icec[j,i]

  def add_icefix(self, ice_land, ice_post, ice_distance):
    j,i = rg12th(self.obs.latitude, self.obs.longitude)
    self.ice_land     = ice_land[j,i]
    self.ice_post     = ice_post[j,i]
    self.ice_distance = ice_distance[j,i]

  def add_ims(self, ims, proj):
    (x,y) = proj(self.obs.longitude, self.obs.latitude)
    #debug: print("add_ims x y = ",x,y, self.obs.longitude, self.obs.latitude, flush=True)
    fi = x/4000. + 6144./2.
    fj = y/4000. + 6144./2.
    i = int(fi+0.5)
    j = int(fj+0.5)
    #debug: print("add_ims", fi, fj,  i,j, flush=True)
    #debug: print("ims ",ims[j,i], flush=True )
    self.ims[0] = ims[j,i]
    self.ims[1] = ims[j,i+1]
    self.ims[2] = ims[j+1,i]
    self.ims[3] = ims[j,i-1]
    self.ims[4] = ims[j-1,i]
    #debug: print(self.ims, flush=True)

  def __getitem__(self, i):
    return(self.obs.tb[i])

#---------------------------------------------------------------
# Reading from a file to a list of matchups
# Read in raw data, customized for each different sort of scan/match
#---------------------------------------------------------------
def raw_read(fin):
  tb_lr = np.zeros((amsr2_lr.ntb))
  sat_lr = amsr2_lr()
  tmp = match(sat_lr)
  lrmatch = []
  for line in fin:
    words = line.split()
    if ("lr" in line):

      icec  = int(words[0])
      land_frac = 1. - float(words[5]) # original has 0 == full land

      satid = int(words[2])
      lat   = float(words[3])
      lon   = float(words[4])
      x = amsr2_lr(satid = satid, latitude = lat, longitude = lon)
      for i in range(0,x.ntb):
        tb_lr[i] = float(words[6+i])
      x.add_tb(tb_lr)

      tmp = match(x, land = land_frac, icec = icec)
      #tmp.show()
      lrmatch.append(tmp)

  return lrmatch
#----------------------------------------------------------
#  Read in from the standardized 'match' class
def matched_read(fin):
  sat_lr = amsr2_lr()
  lrmatch = []
  tmp = match(sat = sat_lr)
  x = match(sat = sat_lr)
  for line in fin:
    tmp.lr_read(line)
    lrmatch.append( x )
    lrmatch[len(lrmatch)-1] = copy.deepcopy(tmp)

  return lrmatch

