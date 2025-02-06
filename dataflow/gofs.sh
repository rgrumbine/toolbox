#!/bin/sh

echo zzz entered gofs.sh

set -x

models=$HOME/noscrub/model_intercompare/
if [ ! -d $models/gofs ] ; then
        mkdir -p $models/gofs
fi      
cd $models/gofs

tag=`date +"%Y%m%d"`
  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`

while [ $tag -gt 20230901 ]
do

  if [ ! -d gofs.$tag ] ; then
    base=/lfs/h1/ops/prod/dcom/$tag/wgrdbul/navy_hycom
    if [ -d $base ] ; then
      time cp -rp $base gofs.$tag
    else
      echo no directory for $tag
    fi
  fi
  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done

echo zzz leaving gofs.sh
