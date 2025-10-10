import sys
from math import *

'''
rerun -- using pre-spliced and analyzed data
      -- an an algorithm already in hand
'''
#-------------------------------------------------------------

thin = int(sys.argv[1])

count = 0

allice  = 0
pcount  = 0

count00 = 0
count01 = 0
count10 = 0
count11 = 0
#debug: print("len = ",len(sys.argv))

for fnum in range (2,len(sys.argv)):
  #debug: print("fnum ",fnum, flush=True)
  #debug: print("fname ",sys.argv[fnum], flush=True)
  fin = open(sys.argv[fnum], 'r')
  for line in fin:
    words = line.split()
    # skip points sst filter would get
    if float(words[8]) > 275.15:
        continue

    mean   = float(words[0])
    sigma  = float(words[1])
    ocount = float(words[2])
    scaled = float(words[3])
    tmean  = float(words[4])
    tsigma = float(words[5])

    if (float(words[9]) > 0 ):
        conc = 1
        allice += 1
    else:
        conc = 0

    #if (tmean <= 269.985 and tmean > 238.155):
    if (tmean <= 268.855 and tmean > 238.135):
      pcount += 1
      if (conc > 0):
        count11 += 1
      else:
        count10 += 1
    else:
      if (conc > 0):
        count01 += 1
    
    count += 1

  fin.close()

print("count = ",count, count/1.e6)
#-------------------------------------------------------------

pclass = float(pcount)/float(count) 
pice_given_class = count11/pcount
print(pcount, allice, pclass, count11/allice, allice/count)

pice             = (count01 + count11)/count

if pice == 0:
  pclass_given_ice = 0
else:
  pclass_given_ice = pice_given_class * pclass / pice
csi = count11/(count11 + count01 + count10)

print("totbayes", "{:.3f}".format(pice) , "{:.3f}".format(pclass) , "{:.3f}".format(pice_given_class) , "{:.3f}".format(pclass_given_ice), "  {:.3f}".format(allice/count), flush=True )
