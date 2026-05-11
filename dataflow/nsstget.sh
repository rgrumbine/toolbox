#!/bin/bash 
#PBS -N nsst
#PBS -o nsst
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=6:00:00
#PBS -l select=1:ncpus=1

set -x
# Span back to 'dawn of time'

base=$HOME/noscrub/nsst
if [ ! -d $base ] ; then
  mkdir -p $base
fi

set -x

export start_date=`date +"%Y%m%d"`
start_date=`expr $start_date - 1`
start_date=`$HOME/bin/dtgfix3 $start_date`
start_date=`expr $start_date - 1`
start_date=`$HOME/bin/dtgfix3 $start_date`

export end_date=20260101

export tag=$start_date
while [ $tag -ge $end_date ]; do

  dcom_dir=${base}/$tag
  export dtag=$tag

  if [ ! -d $dcom_dir ] ; then 

    [ -d $dcom_dir ] || mkdir -p $dcom_dir
    cd $dcom_dir
  
    echo $tag
    yr=`echo $tag | cut -c1-4`
    yrmo=`echo $tag | cut -c1-6`

    set -x
    if [ $tag -ge 20220627 ] ; then
      hpss_dir=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${tag}/com_nsst_v1.2_nsst.$tag.tar
    else
      hpss_dir=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${tag}/com_gfs_prod_sst.$tag.tar
    fi

    htar -xf $hpss_dir 
    set +x
    date

  fi

  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
