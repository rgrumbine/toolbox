import sys
from math import *

'''
rerun -- using pre-spliced and analyzed data
      -- an an algorithm already in hand
'''
#-------------------------------------------------------------

thin = int(sys.argv[1])
fout = open(sys.argv[2],"w")

count = 0

allice  = 0
pcount  = 0

count00 = 0
count01 = 0
count10 = 0
count11 = 0
#debug: print("len = ",len(sys.argv))

for fnum in range (3,len(sys.argv)):
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

    # January (all)
    #if (tmean <= 264.765 and scaled > 105.755): # 96.9% 81.6%
    # February (all)
    #if (tmean <= 263.255 and scaled > 105.750): # 96.5% 78.2%
    # March (all)
    #if (tmean <= 268.685 and scaled > 152.785): 
    # April (all)
    #if (tmean <= 265.935 and scaled > 124.995): 
    # May (all)
    #if (tmean <= 267.995 and tmean > 239.475 ): 
    # June (all)
    #if (tmean <= 271.265 and tmean > 239.425 and mean > 67.385 ) :
    # July (all)
    #if (tmean <= 273.815 and tmean > 237.225 and mean > 85.315 ) :
    # August (all)
    #if (tmean <= 270.525 and tmean > 238.775 ) or (tmean <  273.655 and tmean > 270.525 and scaled > 99.065):
    # September (all)
    #if (tmean <= 269.155 and tmean > 238.255 ): 
    # General (all)
    if (tmean <= 268.525 and scaled > 125.005): 
      print(line,end="",file=fout)
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
