""" 
processing for simple time series of grids 
separate from processing for gridded data in a series due to matrix operations
Summations optimized by Gemini

Robert Grumbine
30 October 2026

"""
import numpy as np
import scipy

# Summation functions -- cross terms for non-orthogonality of harmonics
def sssum(freq1, freq2, n, n0 = 0):
  ''' sssum sum of sin(omega1*t)*sin(omega2*t) terms '''
  t = np.arange(n0, n0 + n)
  return float(np.sum(np.sin(freq1 * t) * np.sin(freq2 * t)))

def scsum(freq1, freq2, n, n0 = 0):
  ''' scsum -- sum of sin(omega1*t)*cos(omega2*t) terms '''
  t = np.arange(n0, n0 + n)
  return float(np.sum(np.sin(freq1*t) * np.cos(freq2*t)))

def ccsum(freq1, freq2, n, n0 = 0):
  ''' ccsum -- sum of cos(omega1*t)*cos(omega2*t) terms '''
  t = np.arange(n0, n0 + n)
  return float(np.sum(np.cos(freq1*t) * np.cos(freq2*t)))

def sumsin(freq, t, n):
  ''' sumsin -- sum of sin(omega*t), t = vector '''
  t = np.arange(0, n)
  return float(np.sum(np.sin(freq*t)))

def sumcos(freq, t, n):
  ''' sumcos -- sum of cos(omega*t), t = vector '''
  t = np.arange(0, n)
  return float(np.sum(np.cos(freq*t)))

#***********************************************************----------!!

def sinsum(n, freq, n0 = 0):
  ''' sinsum -- sum of sin(omega*t), t = regular '''
  t = np.arange(n0, n0 + n)
  return float(np.sum(np.sin(freq*t)))

def cossum(n, freq, n0 = 0):
  ''' cossum -- sum of cos(omega*t), t = regular '''
  t = np.arange(n0, n0 + n)
  return float(np.sum(np.cos(freq*t)))

#***********************************************************----------!!
# x is the data vector, a, b are cos, sin amplitudes, respectively
# this changes in summations for grids

def harmonic_coeffs(coeff, omega, t, m, n0 = 0):
  ''' harmonic_coeffs -- compute the trig sums and load the coefficient matrix '''
  for i in range(0, m):
    for j in range(0, m):
      coeff[2*i  , 2*j  ]  = ccsum(omega[i], omega[j], t, n0)
      coeff[2*i+1, 2*j  ]  = scsum(omega[j], omega[i], t, n0) # note omega[j], omega[i]
      coeff[2*i  , 2*j+1]  = scsum(omega[i], omega[j], t, n0) # note omega[i], omega[j]
      coeff[2*i+1, 2*j+1]  = sssum(omega[i], omega[j], t, n0)

def harmonic_solve(coeff, y, a, b, m):
  ''' harmonic_colve least squares solution for full generality '''
  for i in range(0, y.shape[0]):
    for j in range(0, y.shape[1]):
      z = scipy.linalg.solve(coeff,y[i,j,:])
      for f in range(0,m):
        a[i,j,f] = z[2*f]
        b[i,j,f] = z[2*f+1]
