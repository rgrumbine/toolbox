#!/bin/sh

module load prod_envir

set -x
tag=${tag:-`date +"%Y%m%d"`}
k=0

base=/lfs/h1/ops/dev/dcom
outdir=$HOME/noscrub/thickness

while [ $k -le 7 ] 
do
  if [ ! -f $outdir/${tag}_south_mix_sit_v300.nc ] ; then
    cd $base/$tag
    cd seaice/smos-smap
    cp -p *.nc $outdir
  fi

  k=`expr $k + 1`
  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
