#!/bin/bash --login
#PBS -N cpv16
#PBS -o cpv16
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=1:00:00
#PBS -l select=1:ncpus=1

set -x

cd /u/robert.grumbine/noscrub/gdas.v16


#/lfs/h1/ops/prod/com/gfs/v16.3/gdas.20261029/00/atmos/gdas.t00z.master.grb2f009
#
#gdas.t00z.master.grb2f000

tag=`date +"%Y%m%d"`
while [ $tag -ge 20261020 ] 
do
  
  export base=/lfs/h1/ops/prod/com/gfs/v16.3/gdas.${tag}/00/atmos/

  if [ -d $base ] ; then
    if [ ! -d gdas.${tag}/00/atmos/ ] ; then
      mkdir -p gdas.${tag}/00/atmos/
    fi


    if [ ! -f gdas.${tag}/00/atmos/gdas.t00z.sfluxgrbf000.grib2 ] ; then
      echo getting sflux for $tag
      cp -p $base/gdas.t00z.sfluxgrbf000.grib2 ./gdas.$tag/00/atmos/gdas.t00z.sfluxgrbf000.grib2
    fi

    if [ ! -f  gdas.${tag}/00/atmos/gdas.t00z.master.grb2f000 ] ; then
      echo getting master pgb for $tag
      cp -p $base/gdas.t00z.master.grb2f000 gdas.${tag}/00/atmos/gdas.t00z.master.grb2f000
    fi

  else
    echo no comdir for $tag
  fi
  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
