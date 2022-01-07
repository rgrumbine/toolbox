#!/bin/sh

set -x

start_date=20210501
end_date=`date +"%Y%m%d"`
base=/u/Robert.Grumbine/noscrub/sice

tag=$start_date
while [ $tag -le $end_date ]; do

  dirout=${base}/$tag

  if [  -d $dirout ] ; then 
    if [ ! -f ice5min.grib2.$tag ] ; then
      cp -p $dirout/seaice.t00z.5min.grb.grib2 ice5min.grib2.$tag
    fi
  fi

  #tag=`sh /nwprod/util/ush/finddate.sh $tag d+1`
  tag=`expr $tag + 1`
  tag=`dtgfix3 $tag`
done
