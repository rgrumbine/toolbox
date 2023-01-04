#!/usr/bin/env python3
import argparse
import glob
import os

import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import netCDF4 as nc

import cartopy.crs as ccrs
import cartopy.feature as cfeature

print("hello")

def plot_world_map(lons, lats, data, metadata, plotpath):
    # plot generic world map
    fig = plt.figure(figsize=(12,8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(central_longitude=0))
    ax.add_feature(cfeature.GSHHSFeature(scale='auto'))
    ax.set_extent([-180, 180, -90, 90])
    cmap='jet'
    cbarlabel = '%s' % (metadata['var'])
    plttitle = 'Plot of variable %s' % (metadata['var'])

    vmin = np.nanmin(data)
    vmax = np.nanmax(data)
    cs = ax.pcolormesh(lons, lats, data,vmin=vmin,vmax=vmax,cmap=cmap)
    cb = plt.colorbar(cs, extend='both', orientation='horizontal', shrink=0.5, pad=.04)
    cb.set_label(cbarlabel, fontsize=12)
    plt.title(plttitle)
    plt.savefig(plotpath)
    plt.close('all')

def read_var(datapath, varname):
    datanc  = nc.Dataset(datapath)
    latout  = datanc.variables['latitude'][:]
    lonout  = datanc.variables['longitude'][:]
    dataout = datanc.variables[varname][0,...]
    datanc.close()
    print("dataout max min ",dataout.max(), dataout.min() )
    print("latout max min ",latout.max(), latout.min() )
    print("lonout max min ",lonout.max(), lonout.min() )
    
    #ny = int(180)
    #nx = int(360)
    #latout = np.zeros((ny, nx))
    #lonout = np.zeros((ny, nx))
    #dataout = np.zeros((nx, ny))
    #for j in range(0,ny):
    #  latout[j,:] = float(j)-89.5
    #for i in range(0,nx):
    #  lonout[:,i] = float(i)+0.5
    #dataout = latout

    return dataout, lonout, latout



def gen_figure(inpath, outpath, varname):
    # read the files to get the 2D array to plot
    data, lons, lats = read_var(inpath, varname)
    plotpath = outpath+'/%s.png' % (varname)
    metadata ={  'var': varname,
                }
    plot_world_map(lons, lats, data, metadata, plotpath)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('-o', '--output', help="path to output directory", default="./")
    ap.add_argument('-i', '--input', help="path to input file", required=True)
    ap.add_argument('-v', '--variable', help="variable name to plot", required=True)
    MyArgs = ap.parse_args()
    gen_figure(MyArgs.input, MyArgs.output, MyArgs.variable)
