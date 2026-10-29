#!/bin/sh

# GDAS v16 version
# Robert Grumbine
# 29 October 2026

module load intel wgrib2
#set -x

export HOME=/u/robert.grumbine/

export COMROOT=$HOME/noscrub/gdas.v16/

cd /u/robert.grumbine/rgdev/toolbox/gefs/gdas/ #for prsget flxget

tag=${tag:-`date +"%Y%m%d"`}
d=0
while [ $d -lt 7 ] 
do
  yy=`echo $tag | cut -c1-4`
  mm=`echo $tag | cut -c5-6`
  dd=`echo $tag | cut -c7-8`
  
  base=$COMROOT/gdas.$tag/00/atmos/

  #PRS
  if [ ! -f thinned/prs.${yy}${mm}${dd}.nc ] ; then
    wgrib2 $base/gdas.t00z.master.grb2f000 | grep -f prsget | wgrib2 -i $base/gdas.t00z.master.grb2f000 \
	    -new_grid gaussian 0:1536:0.234375 89.820709:768 a.grib2 
    wgrib2 a.grib2 -netcdf thinned/prs.${yy}${mm}${dd}.nc
    rm a.grib2
  fi
    
  #FLX
  if [ ! -f thinned/flx.${yy}${mm}${dd}.nc ] ; then
    wgrib2 $base/gdas.t00z.sfluxgrbf000.grib2 | grep -f flxget | wgrib2 -i $base/gdas.t00z.sfluxgrbf000.grib2 \
	    -new_grid gaussian 0:1536:0.234375 89.820709:768 b.grib2
    wgrib2 b.grib2 -netcdf thinned/flx.${yy}${mm}${dd}.nc
    rm b.grib2
  fi

  d=`expr $d + 1`
  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
