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


module load HPSS/5.0.2.5    # for hpss
module load prod_envir/1.1.0
module load ips/19.0.5.281  impi/19.0.5 #for prod_util
module load prod_util/1.1.6 # for finddate

# Span back to 'dawn of time'
start_date=`date +"%Y%m%d"`
start_date=20200831
#start_date=`sh finddate.sh $start_date d-1`
#start_date=`sh finddate.sh $start_date d-1`
#end_date=20110101
end_date=20190101
base=/u/Robert.Grumbine/noscrub/imssnow

imsfile=./wgrbbul/imssnow.grb.grib2
ims96file=./wgrbbul/imssnow96.grb.grib2
date=$start_date
j=0
while [ $date -ge $end_date ]; do

  dcom_dir=${base}/$date
# for near real time
  if [ -f /gpfs/dell1/nco/ops/dcom/prod/$date/$imsfile ] ; then
    if [ ! -d $dcom_dir ] ; then
       mkdir -p $dcom_dir/wgrbbul
    fi
    cp -p /gpfs/dell1/nco/ops/dcom/prod/$date/$imsfile $dcom_dir/wgrbbul
  fi
  if [ -f /gpfs/dell1/nco/ops/dcom/prod/$date/$ims96file ] ; then
    if [ ! -d $dcom_dir ] ; then
       mkdir -p $dcom_dir
    fi
    cp -p /gpfs/dell1/nco/ops/dcom/prod/$date/$ims96file $dcom_dir/wgrbbul
  fi


# trying hpss archive:
  if [ ! -d $dcom_dir -a $j -ge 2 ] ; then 

    [ -d $dcom_dir ] || mkdir -p $dcom_dir
  
    echo $date
    yr=`echo $date | cut -c1-4`
    yrmo=`echo $date | cut -c1-6`
  
    #older than ~20100418
    #hpss_dcom=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${date}/dcom_us007003_${date}.tar
    #newer:
    hpss_dcom=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${date}/dcom_prod_${date}.tar
    cd $dcom_dir
   
    set -x
    htar -xf $hpss_dcom $imsfile $ims96file 
    set +x

  fi

  date=`sh finddate.sh $date d-1`
  j=`expr $j + 1`
done
