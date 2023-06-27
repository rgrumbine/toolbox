#!/bin/sh

module purge
for m in bacio bufr craype envvar g2 geos grib_util hdf5 hpc hpss HPSS hsi imagemagick impi intel ips jasper libjpeg libpng netcdf PrgEnv-intel prod_envir prod_util proj python w3nco wgrib2 zlib
do
  echo zzz trying module $m zzz
  module avail $m
done
