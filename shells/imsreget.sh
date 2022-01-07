#!/bin/sh --login
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


module load prod_envir/1.1.0
module load ips/18.0.1.163  # for prod_util
module load prod_util/1.1.3 # for finddate
module load HPSS/5.0.2.5    # for hpss

# Span back to 'dawn of time'
start_date=`date +"%Y%m%d"`
start_date=`sh finddate.sh $start_date d-1`
start_date=`sh finddate.sh $start_date d-1`
#end_date=20110101
end_date=20201101
base=/u/Robert.Grumbine/onoscrub/imssnow

imsfile=./wgrbbul/imssnow.grb.grib2
ims96file=./wgrbbul/imssnow96.grb.grib2

#Should really back up 2 days for the runs from current day
date=$start_date
while [ $date -ge $end_date ]; do

  dcom_dir=${base}/$date

  if [ ! -d $dcom_dir ] ; then 

    [ -d $dcom_dir ] || mkdir -p $dcom_dir
  
    echo $date
    yr=`echo $date | cut -c1-4`
    yrmo=`echo $date | cut -c1-6`
  
    #hpss_dcom=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${date}/dcom_us007003_${date}.tar
    hpss_dcom=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${date}/dcom_prod_${date}.tar
    cd $dcom_dir
   
    set -x
    #/nwprod/util/ush/hpsstar getnostage $hpss_dcom $imsfile $ims96file $imsfile2 $ims96file2
    htar -xf $hpss_dcom $imsfile $ims96file $imsfile2 $ims96file2
    set +x

  fi

  date=`sh finddate.sh $date d-1`
done
