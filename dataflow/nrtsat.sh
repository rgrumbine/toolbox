#!/bin/bash 
#PBS -N satget
#PBS -o satget
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=6:00:00
#PBS -l select=1:ncpus=1

module load prod_envir

#ssmi_file=./b012/xx001
#amsre_file=./b021/xx254
amsr2_file=./b021/xx248
ssmisu_file=./b021/xx201

set -x
#name change 26 Feb 2020
#  what is now dcom_prod was dcom_us007003

start_date=${start_date:-`date +"%Y%m%d"`}

base=$HOME/noscrub/satellites
if [ ! -d $base ] ; then
  mkdir -p $base
fi

set -x

export date=$start_date

  out_dir=${base}/prod/$date

  if [ ! -d $out_dir/b021 ] ; then 

    [ -d $out_dir ] || mkdir -p $out_dir/b021
  
    dcom=$DCOMROOT/${date}/
    cp $dcom/$amsr2_file $dcom/$ssmisu_file $out_dir/b021 

  fi

