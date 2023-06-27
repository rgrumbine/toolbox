#!/bin/sh

echo zzz entered riops.sh

set -x

models=$HOME/noscrub/model_intercompare/
if [ ! -d $models/riops ] ; then
        mkdir -p $models/riops
fi      
cd $models/riops

tag=`date +"%Y%m%d"`
  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`

while [ $tag -gt 20230401 ]
do

  if [ ! -d riops.$tag ] ; then
    base=/lfs/h1/ops/prod/dcom/$tag/wgrbbul/riops
    if [ -d $base ] ; then
      time cp -rp $base riops.$tag
    else
      echo no directory for $tag
    fi
  fi
  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done

echo zzz leaving riops.sh
