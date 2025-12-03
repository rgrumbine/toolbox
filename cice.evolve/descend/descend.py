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

#-------- Begin Execution ------------------------------------------------
#
# Read in full evolutionary control file:
parmset = []
count = 0
fin = open(sys.argv[1], "r")
for line in fin:
  if (';' in line):
    words = line.split(';')
    name = words[0].strip()
    reference = words[1].strip()
    ranges = words[2].strip()

    x = evo_parameters(name, reference, ranges)
    parmset.append(x)
    count += 1
fin.close()

# Read in fatal mutations
fatalities = []
fin = open(sys.argv[2],"r")
for line in fin:
  words = line.split('=')
  name  = words[0].strip()
  val   = words[1].strip()
  tmp   = copy.deepcopy(fatal(name, val))
  fatalities.append(tmp )
fin.close()

# Read in parents:
nos = []
exptnos = open(sys.argv[3], "r")
for k in exptnos:
  nos.append(int(k))
jmax      = int(len(nos))

# Establish basic parameters for conducting evolution:
pvary     = 1./float(count)
nexpt_ref = 120
ndescend  = int(nexpt_ref / jmax)

#debug: print(len(sys.argv), pvary, nexpt_ref, jmax, ndescend, flush=True)
#debug: exit(0)

exptlist = open("exptlist.ts","w")
print("# Test         Grid    PEs        Sets   ",file=exptlist)

# Run over each parent:
for j in range(0, jmax):
  fname = "parents/set_nml.evo"+"{:d}".format(nos[j])
  # Generate descendants:
  for i in range(0, ndescend):
    descent(fname, parmset, pvary, j*ndescend+i, exptlist, fatalities)

exptlist.close()
