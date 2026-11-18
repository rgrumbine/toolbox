#!/bin/bash --login
#PBS -N getv17gdas
#PBS -o getv17gdas
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=6:00:00
#PBS -l select=1:ncpus=1

set -x

cd /u/robert.grumbine/noscrub/gdas.v17
if [ $? -ne 0 ] ; then
  echo could not cd to archive directory
  exit 1
fi

export base=/5year/NCEPDEV/emc-global/emc.glopara/WCOSS2/GFSv17/retrov17_01_realtime
export nrt=/lfs/h2/emc/gfstemp/emc.global/comroot/retrov17_01_realtime

tag=`date +"%Y%m%d"`

while [ $tag -ge 20261112 ]
do
  # try copying first
  if [ ! -f gdas.${tag}/00/model/atmos/master/gdas.t00z.sflux.f000.grib2 ] ; then
    mkdir -p  gdas.${tag}/00/model/atmos/master
    cp -p $nrt/gdas.${tag}/00/model/atmos/master/gdas.t00z.sflux.f000.grib2 gdas.${tag}/00/model/atmos/master/gdas.t00z.sflux.f000.grib2
  fi

  if [ ! -f  gdas.${tag}/00/analysis/atmos/gdas.t00z.master.analysis.grib2 ] ; then
    mkdir -p gdas.${tag}/00/analysis/atmos
    cp -p $nrt/gdas.${tag}/00/analysis/atmos/gdas.t00z.master.analysis.grib2 gdas.${tag}/00/analysis/atmos/gdas.t00z.master.analysis.grib2
  fi

  # htar if not copy
  if [ ! -f gdas.${tag}/00/model/atmos/master/gdas.t00z.sflux.f000.grib2 ] ; then
    htar xvf $base/${tag}00/gdas.tar gdas.${tag}/00/model/atmos/master/gdas.t00z.sflux.f000.grib2
  fi

  if [ ! -f  gdas.${tag}/00/analysis/atmos/gdas.t00z.master.analysis.grib2 ] ; then
    #htar xvf $base/${tag}00/gdas.tar gdas.${tag}/00/model/atmos/master/gdas.t00z.master.analysis.grib2
    #newer: 
    htar xvf $base/${tag}00/gdas.tar gdas.${tag}/00/analysis/atmos/gdas.t00z.master.analysis.grib2
  fi

  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done

