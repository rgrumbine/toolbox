#!/bin/sh

cd $HOME/noscrub/model_intercompare/giops/

tag=`date +"%Y%m%d"`
  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`

while [ $tag -ge 20220801 ]
do

  if [ ! -d giops.$tag ] ; then
    base=/lfs/h1/ops/dev/dcom/$tag/wgrbbul/cmc_giops
    if [ -d $base ] ; then
      time cp -rp $base giops.$tag
    else
      echo no directory for $tag
    fi
  fi
  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
