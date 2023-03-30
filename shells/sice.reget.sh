#!/bin/sh 
#####
# @ job_name=gethpss
# @ output=~/gethpss.out
# @ error=~/gethpss.err
# @ job_cpu_limit=60
# @ wall_clock_limit = 02:00:00
# @ notification = error
## @ environment = COPY_ALL
# @ class=1
# @ queue
#####

module load prod_envir/1.0.2
module load ips/18.0.1.163
module load prod_util/1.1.0
module load HPSS/5.0.2.5


end_date=20201201
start_date=`date +"%Y%m%d"`
start_date=`sh finddate.sh $start_date d-1`
start_date=`sh finddate.sh $start_date d-1`

base=/u/Robert.Grumbine/onoscrub/sice
if [ ! -d $base ] ; then
  mkdir -p $base
fi

set -x
date=$start_date
while [ $date -ge $end_date ]; do

  dirout=${base}/$date

  if [ ! -d $dirout ] ; then 

    [ -d $dirout ] || mkdir -p $dirout
  
    echo $date
    yr=`echo $date | cut -c1-4`
    yrmo=`echo $date | cut -c1-6`

    if [ $date -ge 20200101 ] ; then
      ice_archive=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${date}/com_omb_prod_sice.${date}.tar
    elif [ $date -ge 20190612 ] ; then
      ice_archive=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${date}/gpfs_dell1_nco_ops_com_omb_prod_sice.${date}.tar
    elif [ $date -ge 20161031 ] ; then
      ice_archive=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${date}/com2_omb_prod_sice.${date}.tar
    else
      ice_archive=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${date}/com_omb_prod_sice.${date}.tar
    fi

    cd $dirout
    htar xvf $ice_archive

  fi

  date=`sh finddate.sh $date d-1`
done
