#!/bin/sh

module load wgrib2
module load prod_envir
#set -x

#$COMROOT/gfs/v16.3/gdas.20260822/00/atmos

PDYm7=20260822
tag=$PDYm7
d=0
while [ $d -lt 7 ] 
do
  yy=`echo $tag | cut -c1-4`
  mm=`echo $tag | cut -c5-6`
  dd=`echo $tag | cut -c7-8`
  
  base=$COMROOT/gfs/v16.3/gdas.$tag/00/atmos
  #PRS
  if [ ! -f thinned/prs.${yy}${mm}${dd}.nc ] ; then
    wgrib2 $base/gdas.t00z.master.grb2f000 | grep -f prsget | wgrib2 -i $base/gdas.t00z.master.grb2f000 -netcdf thinned/prs.${yy}${mm}${dd}.nc
  fi
    
  #FLX
  if [ ! -f thinned/flx.${yy}${mm}${dd}.nc ] ; then
    #wgrib2 GFSFLX.${yy}${mm}${dd}.grbf00 | grep -f flxget | wgrib2 -i GFSFLX.${yy}${mm}${dd}.grbf00 -netcdf thinned/flx.${yy}${mm}${dd}.nc
    grep -f flxget $base/gdas.t00z.sfluxgrbf000.grib2.idx | wgrib2 -i $base/gdas.t00z.sfluxgrbf000.grib2 -netcdf thinned/flx.${yy}${mm}${dd}.nc
  fi

  d=`expr $d + 1`
  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done 
