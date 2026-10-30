""" 
processing for simple time series of grids 
separate from processing for gridded data in a series due to matrix operations

Robert Grumbine
30 October 2026

"""
from math import sin, cos
import scipy
import numpy as np

#***********************************************************----------!!
# Summation functions -- cross terms for non-orthogonality of harmonics
def sssum(freq1, freq2, n, n0 = 0):
  ''' sssum sum of sin(omega1*t)*sin(omega2*t) terms '''
  tsum = 0.
  for i in range(n0, n0+n):
    tsum += sin(freq1*i)*sin(freq2*i)
  return tsum

def scsum(freq1, freq2, n, n0 = 0):
  ''' scsum -- sum of sin(omega1*t)*cos(omega2*t) terms '''
  tsum = 0.
  for i in range(n0, n0+n):
    tsum += sin(freq1*i)*cos(freq2*i)
  return tsum

def ccsum(freq1, freq2, n, n0 = 0):
  ''' ccsum -- sum of cos(omega1*t)*cos(omega2*t) terms '''
  tsum = 0.
  for i in range(n0, n0+n):
    tsum += cos(freq1*i)*cos(freq2*i)
  return tsum

#***********************************************************----------!!
def sumsin(n, freq, n0 = 0):
  ''' sumsin -- sum of sin(omega*t), t = regular '''
  tsum = 0.
  for i in range(n0,n0+n):
    tsum += sin(freq*i)
  return tsum

def sumcos(n, freq, n0 = 0):
  ''' sumcos -- sum of cos(omega*t), t = regular '''
  tsum = 0.
  for i in range(n0,n0+n):
    tsum += cos(freq*i)
  return tsum

def sumtsin(n, freq, n0 = 0):
  ''' sinsum -- sum of sin(omega*t), t = regular '''
  tsum = 0.
  for i in range(n0,n0+n):
    tsum += sin(freq*i)
  return tsum

def sumtcos(n, freq, n0 = 0):
  ''' sinsum -- sum of cos(omega*t), t = regular '''
  tsum = 0.
  for i in range(n0,n0+n):
    tsum += cos(freq*i)
  return tsum

#***********************************************************----------!!
# x is the data vector, a, b are cos, sin amplitudes, respectively
# this changes in summations for grids

def harmonic_coeffs(coeff, omega, count, m, n0 = 0):
  ''' harmonic_coeffs -- compute the trig sums and load the coefficient matrix '''
  for i in range(0, m):
    for j in range(0, m):
      coeff[2*i  , 2*j  ]  = ccsum(omega[i], omega[j], count, n0)
      coeff[2*i+1, 2*j  ]  = scsum(omega[j], omega[i], count, n0) # note omega[j], omega[i]
      coeff[2*i  , 2*j+1]  = scsum(omega[i], omega[j], count, n0) # note omega[i], omega[j]
      coeff[2*i+1, 2*j+1]  = sssum(omega[i], omega[j], count, n0)

def harmonic_solve(coeff, y, a, b, m):
  ''' harmonic_solve least squares solution for full generality '''
  condition = scipy.linalg.svdvals(coeff)
  cond_num = condition[0] / condition[-1]
  print("harmonics only condition number = ",cond_num)
  for i in range(0, y.shape[0]):
    for j in range(0, y.shape[1]):
      z = scipy.linalg.solve(coeff,y[i,j,:])
      for f in range(0,m):
        a[i,j,f] = z[2*f]
        b[i,j,f] = z[2*f+1]


#***********************************************************----------!!
# x is the data vector, a, b are cos, sin amplitudes, respectively, augmented by slope and intercept
# this changes in summations for grids

def trend_coeffs(coeff, omega, count, m, n0 = 0):
  ''' harmonic_coeffs -- compute the trig sums and load the coefficient matrix '''
  coeff.fill(0.0)
  for i in range(0, m):
    for j in range(0, m):
      coeff[2*i  , 2*j  ]  = ccsum(omega[i], omega[j], count, n0)
      coeff[2*i+1, 2*j  ]  = scsum(omega[j], omega[i], count, n0) # note omega[j], omega[i]
      coeff[2*i  , 2*j+1]  = scsum(omega[i], omega[j], count, n0) # note omega[i], omega[j]
      coeff[2*i+1, 2*j+1]  = sssum(omega[i], omega[j], count, n0)

  for i in range(0, m):
    coeff[2*i  , 2*m]   = sumcos(count, omega[i], n0)
    coeff[2*i+1, 2*m]   = sumsin(count, omega[i], n0)
    coeff[2*i, 2*m+1]   = sumtcos(count, omega[i], n0)
    coeff[2*i+1, 2*m+1] = sumtsin(count, omega[i], n0)

  for j in range(0, m):
    coeff[2*m, 2*j]   = sumcos(count, omega[j], n0)
    coeff[2*m, 2*j+1] = sumsin(count, omega[j], n0)

  for j in range(0, m):
    coeff[2*m+1, 2*j]   = sumtcos(count, omega[j], n0)
    coeff[2*m+1, 2*j+1] = sumtsin(count, omega[j], n0)

  coeff[2*m, 2*m]      = float(count)
  coeff[2*m, 2*m+1]    = sum(range(n0, count+n0))
  coeff[2*m+1, 2*m ]   = sum(range(n0, count+n0))
  coeff[2*m+1, 2*m+1 ] = (np.arange(n0,count+n0)**2).sum()

def trend_solve(coeff, y, a, b, m):
  ''' gemini version: harmonic_solve least squares solution for full generality '''

  ni, nj, ncoeff = y.shape
  y_flat = y.reshape(-1, ncoeff).T
  z_flat = scipy.linalg.solve(coeff, y_flat)
  condition = scipy.linalg.svdvals(coeff)
  cond_num = condition[0] / condition[-1]
  print("condition number = ",cond_num)

  for f in range(0, m):
      a[:,:,f] = z_flat[2*f].reshape(ni, nj)
      b[:,:,f] = z_flat[2*f+1].reshape(ni, nj)
#***********************************************************----------!!
# x is the data vector, a, b are cos, sin amplitudes, respectively, augmented by slope and intercept
# this changes in summations for grids

def mean_coeffs(coeff, omega, count, m, n0 = 0):
  ''' harmonic_coeffs -- compute the trig sums and load the coefficient matrix '''
  coeff.fill(0.0)
  for i in range(0, m):
    for j in range(0, m):
      coeff[2*i  , 2*j  ]  = ccsum(omega[i], omega[j], count, n0)
      coeff[2*i+1, 2*j  ]  = scsum(omega[j], omega[i], count, n0) # note omega[j], omega[i]
      coeff[2*i  , 2*j+1]  = scsum(omega[i], omega[j], count, n0) # note omega[i], omega[j]
      coeff[2*i+1, 2*j+1]  = sssum(omega[i], omega[j], count, n0)

  for i in range(0, m):
    coeff[2*i  , 2*m]   = sumcos(count, omega[i], n0)
    coeff[2*i+1, 2*m]   = sumsin(count, omega[i], n0)

  for j in range(0, m):
    coeff[2*m, 2*j]   = sumcos(count, omega[j], n0)
    coeff[2*m, 2*j+1] = sumsin(count, omega[j], n0)

  #coeff[2*m+1, 2*m+1]      = float(count)
  coeff[2*m, 2*m]      = float(count)

def mean_solve(coeff, y, a, b, m):
  ''' gemini version: harmonic_solve least squares solution for full generality '''

  ni, nj, ncoeff = y.shape
  y_flat = y.reshape(-1, ncoeff).T
  z_flat = scipy.linalg.solve(coeff, y_flat)
  condition = scipy.linalg.svdvals(coeff)
  cond_num = condition[0] / condition[-1]
  print("condition number = ",cond_num)

  for f in range(0, m):
      a[:,:,f] = z_flat[2*f].reshape(ni, nj)
      b[:,:,f] = z_flat[2*f+1].reshape(ni, nj)
  f = m
  a[:,:,f] = z_flat[2*f].reshape(ni, nj)
