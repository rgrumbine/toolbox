import sys
import csv
from math import *
import numpy
import copy

from evo_parameters import *

"""
Types of parameters and their variation:
* T/F
* List of numbers
* List of character strings (e.g. 'bubbly')
* Arithmetic range e.g. [0,1]
* Logarithmic range e.g. [0.1x, 10x]

name, reference value, variations allowed
for ranges, min/max order on input

"""

#-----------------------------------------------------------------------

parmset = []

# Begin execution
count = 0
for line in open(sys.argv[1], "r"):
  if (';' in line):
    words = line.split(';')
    #debug: print(words, flush=True)

    name = words[0].strip()
    reference = words[1].strip()
    ranges = words[2].strip()
    #debug: print('deb ',name, ';', reference,';',  ranges, flush=True)

    x = evo_parameters(name, reference, ranges)
    parmset.append(x)
    count += 1
#debug: print(count, len(parmset), flush=True )


# Change 1 and only 1 parameter, but ensure that it does get changed
exptlist = open("exptlist.ts","w")
print("# Test         Grid    PEs        Sets   ",file=exptlist)

for k in range(0, count):

  tmp = copy.deepcopy(parmset)
  fout = open("set_nml.evo"+"{:d}".format(k),"w")
  tries = 0
  while ((tmp[k].reference == parmset[k].reference) and (tries < 10) ):
    tmp[k].vary()
    tries += 1
  if ( tries > 9) :
    print("tries = ",tries,tmp[k].type, flush=True)
  else:
    tmp[k].namelist(fname = fout)
    print("smoke  gx3  1x1  med3,yr_out,evo"+"{:d}".format(k),file=exptlist)

  fout.close()


exptlist.close()
