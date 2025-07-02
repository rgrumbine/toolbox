import sys
import numpy as np

fin = open(sys.argv[1],"r")
counts = []
pcts = []
tot=0
for line in fin:
    words = line.split()
    counts.append(tot + int(words[6]))
    pcts.append(float(words[4]))
    tot += int(words[6])

for i in range(0,len(counts)):
  print(i,pcts[i], counts[i]/tot)

#175 leaf 0.863 0.001 0.863 0.001 5565 0.0011524199057811305 0.863
