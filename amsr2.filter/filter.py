# python system
import os
import sys
import copy
from math import *
import datetime

# shared
from match import *
from tools import *
from filtering import *


"""
Read in f01, f10 files, and f11, f00 files

Apply filter(s)

Write out residual files

"""

x = amsr2_lr(satid = 0, latitude = 0., longitude = 0.)
tmp = match.match(x)

#---------------------------------------------------------------

# Filter:
#class tbfilt:
class tbfilt:

  def __init__(self, tchan, tcrit, quality, frequency):
    self.chan = tchan
    self.tcrit = tcrit
    self.quality = quality
    self.frequency = frequency

  def show(self, fout = sys.stdout):
    print(self.chan, self.tcrit, self.quality, self.frequency, file=fout)

  # x = a matchup
  def apply(self, x):
    if (x.obs[self.chan] > self.tcrit):
      return True
    return False

#  def read(self, fin):
#
#  def better(self, other):
#  
#  def nondom(self, other):

def apply_filters(filts, matchups, show = True):
  applied = int(0)
  nfilt = len(filts)
  for k in range(int(0), len(matchups)):
    to_filter = False
    for ifilt in range(0, nfilt): 
      if (filts[ifilt].apply(matchups[k])):
        to_filter = True
        if (show):
          print("filt ",ifilt, "match k",k, matchups[k].show(), flush=True )
    if(to_filter):
      applied += 1
  #debug: print("tot applied: ",applied,flush=True)
  return applied
        


#tchn, tb_crit, bayes_out, p(tb> tbcrit), pbogus, p(tb > tbcrit | bogus)
#
#best are:
#  bayes_out highest, frequency highest P(bogus | tb_k > tbcrit) -- almost certainly is_bogus
#  bayes_out lowest, frequency highest -- almost certainly is_not_bogus
fin = open(sys.argv[1], "r")
tfilters = []
tmp = tbfilt(0,0,0,0)

# Read in all infos
k = 0
for line in fin:
  words = line.split()
  tmp = tbfilt(float(words[2]), float(words[3]), float(words[4]), float(words[5]) )
  tfilters.append(tmp)
  tfilters[k] = copy.deepcopy(tmp)
  k += 1

# go through filters
for tchan in range(0, x.ntb):
  #debug: print("tchan = ",tchan, flush=True)
  is_bogus = tbfilt(tchan, 0, 0.5, 0.)
  is_not_bogus = tbfilt(tchan, 1, 0.5, 0.)
  best_bogus = is_bogus
  best_not_bogus = is_not_bogus
  nondom_bogus = []
  nondom_not_bogus = []
  nondom_bogus.append(is_bogus)
  nondom_not_bogus.append(is_not_bogus)

  #Find the best filters (is, is_not)
  for k in range(0, len(tfilters)):
    if (tfilters[k].chan == tchan):
      #debug: tfilters[k].show()
      if (tfilters[k].quality > best_bogus.quality and tfilters[k].frequency > best_bogus.frequency):
        best_bogus = tfilters[k]
        #debug: best_bogus.show()
      if (tfilters[k].quality < best_not_bogus.quality and tfilters[k].frequency > best_not_bogus.frequency):
        best_not_bogus = tfilters[k]
        #debug: best_not_bogus.show()
        
  #Find filters which are not dominated by 
  for k in range(0, len(tfilters)):
    if (tfilters[k].chan == tchan):
      if (tfilters[k].quality >= best_bogus.quality or tfilters[k].frequency >= best_bogus.frequency):
        nondom_bogus.append(tfilters[k])
      if (tfilters[k].quality <= best_not_bogus.quality or tfilters[k].frequency >= best_not_bogus.frequency):
        nondom_not_bogus.append(tfilters[k])


  best_bogus.show()
  best_not_bogus.show()
  print("tchan",tchan, len(nondom_bogus), len(nondom_not_bogus), "\n", flush=True)



#tbfilt = tchan, tcrit, null, null -- to apply filter only need tchan, tcrit)
# Filters that should indicate _not ice_
filt = []
filt.append(tbfilt(0, 283, 0., 0.))
filt.append(tbfilt(1, 274, 0., 0.))
filt.append(tbfilt(2, 274, 0., 0.))
filt.append(tbfilt(3, 275, 0., 0.))
filt.append(tbfilt(4, 277, 0., 0.))
filt.append(tbfilt(5, 282, 0., 0.))
filt.append(tbfilt(6, 278, 0., 0.))
filt.append(tbfilt(7, 282, 0., 0.))
filt.append(tbfilt(8, 283, 0., 0.))
filt.append(tbfilt(9, 283, 0., 0.))
filt.append(tbfilt(10, 283, 0., 0.))
filt.append(tbfilt(11, 284, 0., 0.))
nfilt = len(filt)
print("nfilt = ",nfilt)
#exit(0)

#---------------------------------------------------------------
# Read in matchup data sets and see filter effect:
x = amsr2_lr(satid = 0, latitude = 0., longitude = 0.)
tmp = match.match(x)

match11 = []
match10 = []
match01 = []
match00 = []


f11 = open("f11", "r")
f00 = open("f00", "r")
f10 = open("f10", "r")
f01 = open("f01", "r")

applied = int(0)

k = int(0)
for line in f11:
  tmp.lr_read(line)
  to_filter = False
  for ifilt in range(0,nfilt):
    if (filt[ifilt].apply(tmp)):
      #debug: print("applied f11 ",ifilt, "match k",k, tmp.show(), flush=True )
      to_filter = True
  if(to_filter):
    applied += 1
  if (not to_filter):
    match11.append(tmp)
    match11[k] = copy.deepcopy(tmp)
    k += 1
#exit(0)
print("f11 tot applied: ",applied,flush=True)

k = int(0)
for line in f00:
  tmp.lr_read(line)
  to_filter = False
  for ifilt in range(0,nfilt):
    if (filt[ifilt].apply(tmp)):
      #debug: print("applied f00",ifilt, "match k",k, tmp.show(), flush=True )
      to_filter = True
  if(to_filter):
    applied += 1
  if (not to_filter):
    match00.append(tmp)
    match00[k] = copy.deepcopy(tmp)
    k += 1
#exit(0)
print("f00 tot applied: ",applied,flush=True)

k = int(0)
for line in f10:
  tmp.lr_read(line)
  to_filter = False
  for ifilt in range(0,nfilt):
    if (filt[ifilt].apply(tmp)):
      #debug: print("applied f10",ifilt, "match k",k, tmp.show(), flush=True )
      to_filter = True
  if(to_filter):
    applied += 1
  if (not to_filter):
    match10.append(tmp)
    match10[k] = copy.deepcopy(tmp)
    k += 1
#exit(0)
print("f10 tot applied: ",applied,flush=True)

k = int(0)
for line in f01:
  tmp.lr_read(line)
  to_filter = False
  for ifilt in range(0,nfilt):
    if (filt[ifilt].apply(tmp)):
      #debug: print("applied f01",ifilt, "match k",k, tmp.show(), flush=True )
      to_filter = True
  if(to_filter):
    applied += 1
  if (not to_filter):
    match01.append(tmp)
    match01[k] = copy.deepcopy(tmp)
    k += 1
print("f01 tot applied: ",applied,flush=True)

f11.close()
f10.close()
f01.close()
f00.close()

print("after tmax filtering 11 10 01 00: ",len(match11), len(match10), len(match01), len(match00), flush=True )

#---------------------------------
# Now have matchups and initial crudest filters, try applying the 'probably not bogus ice' filters:
#tb(chan) > tcrit --> very unlikely to be bogus ice
notbogus = []
notbogus.append(tbfilt(0, 219, 0.007163580128573802, 0.24996775287239043))
notbogus.append(tbfilt(2, 220, 0.007335094246130854, 0.24983936337980248))
notbogus.append(tbfilt(4, 219, 0.007972289464268666, 0.25727077883102867))
notbogus.append(tbfilt(1, 244, 0.0088876028904507, 0.2622280508877644))
notbogus.append(tbfilt(3, 244, 0.009104451918254437, 0.26793489394788306))
notbogus.append(tbfilt(6, 227, 0.009975999735735106, 0.1752939879773124))
notbogus.append(tbfilt(5, 244, 0.010314302987781668, 0.267519375232369))
#notbogus.append(tbfilt(8, 228, 0.014535480337585087, 0.17609347713488963)
#notbogus.append(tbfilt(7, 248, 0.016869512877848936, 0.18510789709192807)
#notbogus.append(tbfilt(9, 249, 0.022849642062787896, 0.14785617501544468)
#notbogus.append(tbfilt(10, 229, 0.025493605912376247, 0.144787206895574)
#notbogus.append(tbfilt(11, 246, 0.05070844552071158, 0.13341185791775803)

nfilt=len(notbogus)
show = False
print("len notbogus filters: ",len(notbogus), "\n")

print("tot match 00 ",len(match00), end="" )
n = apply_filters(notbogus, match00, show)
print(" filter applied: ",n, float(n)/float(len(match00)) )

print("tot match 01 ",len(match01), end="" )
n = apply_filters(notbogus, match01, show)
print(" filter applied: ",n, float(n)/float(len(match01)) )

print("tot match 10 ",len(match10), end=""  )
n = apply_filters(notbogus, match10, show)
print(" filter applied: ",n, float(n)/float(len(match10)) )

print("tot match 11 ",len(match11), end="" )
n = apply_filters(notbogus, match11, show)
print(" filter applied: ",n, float(n)/float(len(match11)) )

