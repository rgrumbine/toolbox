import sys
import os
import datetime

from math import *
import numpy as np
import numpy.ma as ma

#--------------------------------------------------------
"""
Functions present:

def find(lons, lats, lonin, latin):
def kmlout_path(fname, G, path):

def calculate_distance(lat1, lon1, lat2, lon2):
def cost(case, lat1 = 0, lon1 = 0, lat2 = 0, lon2 = 0, i1 = 0, j1 = 0, 
               i2 = 0, j2 = 0, aice = 0, hi = 0):
def calculateCost(PolarClass, iceCon, iceThick):

"""
#--------------------------------------------------------
def find(lons, lats, lonin, latin):
  tmpx = lons - lonin
  tmpy = lats - latin

  xmask = ma.masked_outside(tmpx, -0.5, 0.5)
  xin = xmask.nonzero() 
  wmask = ma.logical_and(xmask, ma.masked_outside(tmpy, +0.5, -0.5) )
  win = wmask.nonzero()

  imin = -1 
  jmin = -1
  dxmin = 999.
  dymin = 999.
  dmin  = 999.
  for k in range(0, len(win[0]) ):
    i = win[1][k]
    j = win[0][k] 
    if (sqrt(tmpx[j,i]**2 + tmpy[j,i]**2) < dmin):
      imin = i
      jmin = j
      dxmin = abs(tmpx[j,i])
      dymin = abs(tmpy[j,i])
      dmin  = sqrt(tmpx[j,i]**2 + tmpy[j,i]**2)
  return (imin,jmin)
#--------------------------------------------------------
# Polar ship class
#debug: PC = int(input("What is the polar class of the ship vessel? (1-7)\n"))
PC = 1
PossAnswers = [1, 2, 3, 4, 5, 6, 7]
if(PC not in PossAnswers):
  raise Exception("Please select an answer between 1 and 7.")

def calculateCost(PolarClass, iceCon, iceThick):
    #RIO = (aice*10)RV
    #If aice <= .1, return 0
    #If RIO < 0, return 99999
    cost = 1
    return 1.

    #Considered Ice-Free
    if(iceCon <= .1):
        return 0

    if(PolarClass == 1 or PolarClass == 2 or PolarClass == 3 or PolarClass == 4):
        if(iceThick <= 70):
            cost = 3*(iceCon * 10)
        elif(iceThick <= 120):
            cost = 2*(iceCon * 10)
        else:
            cost = (iceCon * 10)
    elif(PolarClass == 5 or PolarClass == 6):
        if(iceThick <= 70):
            cost = 3*(iceCon * 10)
        elif(iceThick <= 95):
            cost = 2*(iceCon * 10)
        elif(iceThick <= 120):
            cost = iceCon*10
        else:
            return 999
    else:
        if(iceThick <= 30):
            cost = 3*(iceCon * 10)
        elif(iceThick <= 50):
            cost = 2*(iceCon * 10)
        elif(iceThick <= 70):
            cost = iceCon*10
        else:
            return 999
    return cost

#Calculates the distance of two points based on the longitude and latitude points of each point
def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    earth_radius = 6371

    # Convert latitude and longitude from degrees to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Calculate the distance
    distance = earth_radius * c

    return distance

def cost(case, lat1 = 0, lon1 = 0, lat2 = 0, lon2 = 0, i1 = 0, j1 = 0, i2 = 0, j2 = 0, aice = 0, hi = 0):
  if (case == 1):
    return 1.
  elif (case == 2):
    if (lon1 == 0 and lat1 == 0 and lon2 == 0 and lat2 == 0):
      print("Must give lat,lon of points to compute distance weighting")
      return 1
    else:
      return calculate_distance(lat1, lon1, lat2, lon2)
  elif (case == 3):
    if (i1 == 0 and i2 == 0 and j1 == 0 and j2 == 0):
      print("Must give i,j of points when weighting by polar class")
      return 1
    else:
      return 1 
  elif (case == 4):
    if (lon1 == 0 and lat1 == 0 and lon2 == 0 and lat2 == 0):
      print("Must give lat,lon of points to compute concentration-distance weighting")
      return 1.
    else:
      return 1.1*calculate_distance(lat1, lon1, lat2, lon2) / (1.1 - aice)

  else:
    print("unknown case, =",case)
    return 1

#--------------------------------------------------------
def kmlout_path(fname, G, path):
  kmlout = open(fname,"w")
  #Print header:
  print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>", file=kmlout)
  print("<kml xmlns=\"http://www.opengis.net/kml/2.2\" xmlns:gx=\"http://www.google.com/kml/ext/2.2\">", file=kmlout)
  print("<Folder>", file=kmlout)
  print("<LookAt>", file=kmlout)
  print("  <range>3000000</range>", file=kmlout)
  print("  <latitude> 68.0 </latitude>", file=kmlout)
  print("  <longitude> -127</longitude>", file=kmlout)
  print("</LookAt>", file=kmlout)
  print("    <Document id=\"1\">", file=kmlout)
  
  for k in range(0,len(path)):
    if (G.nodes[path[k]]['lon'] > 180.):
      tlon = G.nodes[path[k]]['lon']  - 360.
    else:
      tlon = G.nodes[path[k]]['lon']
    print("<Placemark> <Point> <coordinates>",tlon,G.nodes[path[k]]['lat'],0.0,
          "</coordinates></Point></Placemark>", file=kmlout)
  
  #Print footer:
  print("    </Document>",file=kmlout)
  print("</Folder>",file=kmlout)
  print("</kml>",file=kmlout)
  kmlout.close()
#--------------------------------------------------------
def wrap_lons(lons):

  if (lons.max() > 360. or lons.min() < -360. ):
    lmask = ma.masked_array(lons > 2.*360.+180.)
    lin = lmask.nonzero()
    for k in range(0, len(lin[0])):
      i = lin[1][k]
      j = lin[0][k]
      lons[j,i] -= 3.*360.
  
    lmask = ma.masked_array(lons > 1.*360.+180.)
    lin = lmask.nonzero()
    for k in range(0, len(lin[0])):
      i = lin[1][k]
      j = lin[0][k]
      lons[j,i] -= 2.*360.
  
    #most (10.6 million of 14.7 million) rtofs points have lons > 180, so subtract 360 and
    # then correct the smaller number that are < -180 as a result
    lons -= 360.
    lmask = ma.masked_array(lons < -180.)
    lin = lmask.nonzero()
    #print("180 lons ",len(lin), len(lin[0]))
    for k in range(0, len(lin[0])):
      i = lin[1][k]
      j = lin[0][k]
      lons[j,i] += 1.*360.
  
  if ( lons.max() > 180. ):
      lons -= 360.
