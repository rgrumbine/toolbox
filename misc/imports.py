import argparse
import csv
import datetime
from datetime import datetime, timedelta
from ftplib import FTP
import glob
import math
from math import *
import os
import pstats
import sys 
import urllib.request


import matplotlib
import matplotlib.colors as colors
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

import scipy
from scipy.ndimage.filters import gaussian_filter

from netCDF4 import Dataset
from netCDF4 import Dataset,  num2date
import netCDF4

from PIL import Image
from shutil import copy2

import numpy
import numpy as np
import numpy.ma as ma

import pyproj
import shutil 
import tarfile

import cartopy.crs as ccrs
import cartopy.feature as cfeature

#import ncepgrib2
import pygrib # -- on wcoss2 replaced/substituted by ncepgrib2

import networkx as netx

from docx import Document
from docx.shared import Inches
from pptx import Presentation

exit(0)

#Relict -- replace with pyproj et al.
import mpl_toolkits.basemap as basemap
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.basemap import shiftgrid
