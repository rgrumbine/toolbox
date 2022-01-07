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

module load prod_envir/1.0.2
module load ips/18.0.1.163
module load prod_util/1.1.0
module load HPSS/5.0.2.5


ssmi_file=./b012/xx001
amsre_file=./b021/xx254
amsr2_file=./b021/xx248
ssmisu_file=./b021/xx201

set -x
# Span back to 'dawn of time'
#name change 26 Feb 2020
end_date=20210401
start_date=`date +"%Y%m%d"`
start_date=`sh finddate.sh $start_date d-1`
start_date=`sh finddate.sh $start_date d-1`
#start_date=20200601

base=/u/Robert.Grumbine/noscrub/satellites
if [ ! -d $base ] ; then
  mkdir -p $base
fi

date=$start_date
while [ $date -ge $end_date ]; do

  dcom_dir=${base}/prod/$date

  if [ ! -d $dcom_dir ] ; then 

    [ -d $dcom_dir ] || mkdir -p $dcom_dir
  
    echo $date
    yr=`echo $date | cut -c1-4`
    yrmo=`echo $date | cut -c1-6`
  
    hpss_dcom=/NCEPPROD/hpssprod/runhistory/rh${yr}/${yrmo}/${date}/dcom_prod_${date}.tar

    cd $dcom_dir
    date
    set -x
    #/nwprod/util/ush/hpsstar getnostage $hpss_dcom $ssmi_file $amsr2_file $amsre_file $ssmisu_file
    htar -xf $hpss_dcom $ssmi_file $amsr2_file $amsre_file $ssmisu_file
    set +x
    date

  fi

  date=`sh finddate.sh $date d-1`
done
