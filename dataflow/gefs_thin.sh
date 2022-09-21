#!/bin/sh --login
#set -xe
set -e

module load intel
module load libjpeg
module load grib_util
module load wgrib2

cd $HOME/noscrub/gefs/


cyc=00
tag=20220601
end=`date +"%Y%m%d"`
#end=20220810

while [ $tag -le $end ]
do
  echo working on $tag
  winddir=gefs.${tag}/${cyc}/pgrb2ap5_bc
  if [ -d $winddir -a \( ! -f winds.${tag}.tar \) ] ; then
    hhh=000
    while [ $hhh -le 384 ]
    do
      for mem in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20
      do
    
        if [ -f ${winddir}/gep${mem}.t00z.pgrb2a.0p50_bcf${hhh} ] ; then
          grep 'GRD:10 m above ' ${winddir}/gep${mem}.t00z.pgrb2a.0p50_bcf${hhh}.idx | \
             $WGRIB2 -i ${winddir}/gep${mem}.t00z.pgrb2a.0p50_bcf${hhh} -grib wind${mem}.$hhh 
        fi
        
      done
      hhh=`expr $hhh + 3`
      if [ $hhh -lt 100 ] ; then
        hhh=0$hhh
      fi
      if [ $hhh -lt 10 ] ; then
        hhh=0$hhh
      fi
    
    done
    tar cf winds.${tag}.tar wind??.???
    rm wind??.???
  fi

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done

$HOME/rgdev/toolbox/dataflow/gefs_clean.sh
