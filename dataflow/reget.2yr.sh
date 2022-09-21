#!/bin/bash --login
#PBS -N reget5
#PBS -o reget5
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=6:00:00
#PBS -l select=1:ncpus=1

set -x

ssmi_file=./b012/xx001
amsre_file=./b021/xx254
amsr2_file=./b021/xx248
ssmisu_file=./b021/xx201

set -x
# Span back to 'dawn of time'
#name change 26 Feb 2020
#  what is now dcom_prod was dcom_us007003

end_date=20190101
start_date=`date +"%Y%m%d"`
start_date=`expr $start_date - 1`
start_date=`$HOME/bin/dtgfix3 $start_date`
start_date=`expr $start_date - 1`
start_date=`$HOME/bin/dtgfix3 $start_date`
start_date=20190626

base=$HOME/noscrub/satellites
if [ ! -d $base ] ; then
  mkdir -p $base
fi

date=$start_date
while [ $date -ge $end_date ]; do

  dcom_dir=${base}/prod/$date
  if [ $date -le 20200226 ] ; then
	  export dtag=us007003
  else
	  export dtag=prod
  fi

  if [ ! -d $dcom_dir ] ; then 

    [ -d $dcom_dir ] || mkdir -p $dcom_dir
  
    echo $date
    yr=`echo $date | cut -c1-4`
    yrmo=`echo $date | cut -c1-6`
  
    hpss_dcom=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${date}/dcom_${dtag}_${date}.tar

    cd $dcom_dir
    date
    set -x
    #/nwprod/util/ush/hpsstar getnostage $hpss_dcom $ssmi_file $amsr2_file $amsre_file $ssmisu_file
    htar -xf $hpss_dcom $ssmi_file $amsr2_file $amsre_file $ssmisu_file
    set +x
    date

  fi

  date=`expr $date - 1`
  date=`$HOME/bin/dtgfix3 $date`
done
