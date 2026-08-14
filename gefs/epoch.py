''' class for working on epoch-based climatology '''
import datetime
import copy
from math import pi

import netCDF4 as nc
import numpy as np

class epoch:
    ''' class epoch holds epoch date, length of year, and harmonic amplitudes and phases '''
    loy = 365.2422
    epoch = datetime.datetime(1994,1,1)
    nfreq = 6
    freq  = np.zeros((nfreq))

    for i in range(0, nfreq):
        freq[i] = 2.*pi/loy*(i+1)

    def __init__(self, fname, nx=1536, ny=768):
        data = nc.Dataset(fname,'r')
        self.nx = nx
        self.ny = ny
        self.slope     = data.variables['slope'][:,:]
        self.intercept = data.variables['intercept'][:,:]
        self.ampl = np.zeros((self.nfreq, ny, nx))
        self.phas = np.zeros((self.nfreq, ny, nx))
        self.ampl[0] = data.variables['cpy1_amp'][:,:]
        self.ampl[1] = data.variables['cpy2_amp'][:,:]
        self.ampl[2] = data.variables['cpy3_amp'][:,:]
        self.ampl[3] = data.variables['cpy4_amp'][:,:]
        self.ampl[4] = data.variables['cpy5_amp'][:,:]
        self.ampl[5] = data.variables['cpy6_amp'][:,:]

        self.phas[0] = data.variables['cpy1_pha'][:,:]
        self.phas[1] = data.variables['cpy2_pha'][:,:]
        self.phas[2] = data.variables['cpy3_pha'][:,:]
        self.phas[3] = data.variables['cpy4_pha'][:,:]
        self.phas[4] = data.variables['cpy5_pha'][:,:]
        self.phas[5] = data.variables['cpy6_pha'][:,:]


    def climo(self, ftag):
        ''' climo(tag) -- return epoch-based climatology for date 'tag' '''
        fsst = copy.deepcopy(self.intercept)
        delta = (ftag - self.epoch).days
        fsst += self.slope*delta
        for i in range(0,self.nfreq):
            fsst += self.ampl[i]*np.cos(self.phas[i]*pi/180. + self.freq[i]*delta)
        return fsst

class climate:

    def __init__(self):
      self.x = []
      self.x.append( epoch('epoch1994_icetk.nc') )
      self.x.append( epoch('epoch1994_icec.nc') )
      self.x.append( epoch('epoch1994_sst.nc') )
      self.x.append( epoch('epoch1994_uswrf.nc') )

      self.x.append( epoch('epoch1994_prmsl.nc') )
      self.x.append( epoch('epoch1994_z1mb.nc') )
      self.x.append( epoch('epoch1994_z10mb.nc') )
      self.x.append( epoch('epoch1994_z200mb.nc') )
      self.x.append( epoch('epoch1994_z500mb.nc') )
      self.x.append( epoch('epoch1994_z700mb.nc') )
      self.x.append( epoch('epoch1994_z850mb.nc') )

class climate2:

    def __init__(self):
      self.x = []
      self.x.append( epoch('epoch1994_icetk.nc') )
      self.x.append( epoch('epoch1994_icec.nc') )
      self.x.append( epoch('epoch1994_sst.nc') )
      self.x.append( epoch('epoch1994_uswrf.nc') )
      self.x.append( epoch('epoch1994_tmps.nc') )
      self.x.append( epoch('epoch1994_tmp2m.nc') )
      self.x.append( epoch('epoch1994_spfh2m.nc') )
      self.x.append( epoch('epoch1994_u10m.nc') )
      self.x.append( epoch('epoch1994_v10m.nc') )
      self.x.append( epoch('epoch1994_shtfl.nc') )
      self.x.append( epoch('epoch1994_lhtfl.nc') )
      self.x.append( epoch('epoch1994_pwat.nc') )
      self.x.append( epoch('epoch1994_land.nc') )

      self.x.append( epoch('epoch1994_prmsl.nc') )
      self.x.append( epoch('epoch1994_z1mb.nc') )
      self.x.append( epoch('epoch1994_z10mb.nc') )
      self.x.append( epoch('epoch1994_z200mb.nc') )
      self.x.append( epoch('epoch1994_z500mb.nc') )
      self.x.append( epoch('epoch1994_z700mb.nc') )
      self.x.append( epoch('epoch1994_z850mb.nc') )

#atm = climate()
#
#ny = 768
#nx = 1536
#Xavg = np.zeros((ny, nx, 11))
#
#tag = datetime.datetime(1994,1,1)
#for i in range(0, len(atm.x)):
#    Xavg[:,:,i] = atm.x[i].climo(tag)
#    print(i,Xavg[:,:,i].max(), Xavg[:,:,i].min() )
