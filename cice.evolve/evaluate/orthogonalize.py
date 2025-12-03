import copy
from math import *

import numpy
import scipy

"""
#gram-schmidt type orthogonalization, assuming that only elements > column i need to be updated
  y' = y - (y dot x) / (norm(x)*norm(x)) * x
  y'_j = y_j - (y_j dot y_i) / (norm(y_i)*norm(y_i)) * y_i
"""
def gsorthog(mat, i, ncol):
  
  newmat = numpy.zeros((len(mat[:,0]),len(mat[0,:]) ))
  # Copy over old rows
  for k in range(0,i+1):
    newmat[:,k] = copy.deepcopy(mat[:,k])

  x = mat[:,i]
  for j in range(i+1, ncol):
    yj = mat[:,j] - numpy.dot(x,mat[:,j])/ numpy.dot(x,x) * x
    newmat[:,j] = copy.deepcopy(yj)
    #debug: print(j, sqrt(numpy.dot(yj, yj)), flush=True )
  
  return newmat

def correlation_matrix(scoresin, nstat):
# Print out dot product columns i [0:8] vs. j [i,8]
  cormat = numpy.zeros((nstat, nstat))
  for i in range (0, nstat):
    for j in range (i, nstat):
      cor = numpy.dot(scoresin[:,i], scoresin[:,j])
      cormat[i,j] = cor
      cormat[j,i] = cor
      #debug: print("i, j, dot: ",i,j,cor, flush=True)
  for i in range(0, nstat):
    print(i,cormat[i,:].sum() )

  return cormat

# swap j in to i
def swap(mat, i, j):
  tmp = copy.deepcopy(mat[:,i])
  mat[:,i] = copy.deepcopy(mat[:,j])
  mat[:,j] = copy.deepcopy(tmp)

def normalize(matin):
  # Normalize each statistic:
  sums = numpy.zeros((nstat))
  for k in range (0, nexpt):
    for i in range (0, nstat):
      sums[i] += matin[k,i]**2
  # scaling factor:
  for i in range (0, nstat):
    sums[i] = sqrt(sums[i])
    #debug: print("scaling ",i,sums[i], flush=True)
    matin[:,i] /= sums[i]

#---------------------------------------------------------
nexpt = 175
nstat = 9
scores = numpy.zeros((nexpt,nstat))
#fin = open("alpha.2", "r")
fin = open("gamma", "r")
names = [ 'NHmean', 'NHstdev', 'NHmae', 
          'SHmean', 'SHstdev', 'SHmae', 
          'GLmean', 'GLstdev', 'GLmae'
         ]

k = 0
for line in fin:
  words = line.split()
  for i in range (0,nstat):
    scores[k,i] = float(words[3+i])
  k += 1

normalize(scores)
cormat = correlation_matrix(scores, nstat)
#debug: print(cormat, flush=True)

#----------------------------------------------
print("\n round1")
print("orthogonalizing wrt label ",names[0])
round2 = gsorthog(scores, 0, nstat)
swap(round2, 4, 1)
tn = copy.deepcopy(names[1])
names[1] = copy.deepcopy(names[4])
names[4] = copy.deepcopy(tn)
correlation_matrix(round2, nstat)

print("\n round2")
print("orthogonalizing wrt label ",names[1])
round3 = gsorthog(round2, 1, nstat)
swap(round3, 6, 2)
tn = copy.deepcopy(names[2])
names[2] = copy.deepcopy(names[6])
names[6] = copy.deepcopy(tn)
correlation_matrix(round3, nstat)

print("\n round3")
print("orthogonalizing wrt label ",names[2])
round4 = gsorthog(round3, 2, nstat)
zzz = correlation_matrix(round4, nstat)

