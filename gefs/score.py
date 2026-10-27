import sys
import datetime


import numpy as np
import matplotlib
import matplotlib.pyplot as plt

#-------------------------------------------------------------------------
wins_p = np.zeros((52 + 1))
wins_c = np.zeros((52 + 1))
wins_coverp = np.zeros((52 + 1))

with open(sys.argv[1],"r") as fin:
  for line in fin:
      words  = line.split()
      lead   = int(words[1])
      rms_p  = float(words[3])
      rms_ai = float(words[5])
      rms_c  = float(words[7])
      if rms_ai < rms_p:
        wins_p[lead] += 1 
      if rms_ai < rms_c:
        wins_c[lead] += 1 
      if rms_c < rms_p:
        wins_coverp[lead] += 1

for k in range(1,53):
    print(k, wins_p[k], wins_c[k], wins_coverp[k])

