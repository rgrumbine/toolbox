#!/bin/bash 
#PBS -N imsreget
#PBS -o imsreget
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=6:00:00
#PBS -l select=1:ncpus=1

set -x

module load prod_envir
start_date=${start_date:-`date +"%Y%m%d"`}

ims4km=./wgrbbul/imssnow96.grb
ims4km_grib2=./wgrbbul/imssnow96.grb.grib2

base=$HOME/noscrub/satellites/prod
if [ ! -d $base ] ; then
  mkdir -p $base
fi

set -x

export date=$start_date

  out_dir=${base}/$date/wgrbbul

  if [ ! -f $out_dir/$ims4km_grib2 ] ; then 

    [ -d $out_dir ] || mkdir -p $out_dir
  
    hpss_dcom=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${date}/dcom_${dtag}.tar
    cp $DCOMROOT/$date/$ims4km $DCOMROOT/$date/$ims4km_grib2 $out_dir

  fi

