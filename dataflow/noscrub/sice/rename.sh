#!/bin/bash --login
#PBS -N sicereget
#PBS -o sicereget
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=6:00:00
#PBS -l select=1:ncpus=1

set -x

#Go back to this date, ensuring all are present:
end_date=20191231

#Start from this date -- back up 2 days for archive process/delay
start_date=`date +"%Y%m%d"`
##start_date=`sh finddate.sh $start_date d-1`
##start_date=`sh finddate.sh $start_date d-1`

start_date=`expr $start_date - 1`
start_date=`$HOME/bin/dtgfix3 $start_date`
start_date=`expr $start_date - 1`
start_date=`$HOME/bin/dtgfix3 $start_date`

start_date=20210831

base=$HOME/noscrub/sice/
if [ ! -d $base ] ; then
  mkdir -p $base
fi
cd $base

set -x
date=$start_date
while [ $date -ge $end_date ]; do

  dirout=${base}/sice.$date

  if [ -d $date ] ; then
    mv $date sice.$date
  fi

  #date=`sh finddate.sh $date d-1`
  date=`expr $date - 1`
  date=`$HOME/bin/dtgfix3 $date`
done


