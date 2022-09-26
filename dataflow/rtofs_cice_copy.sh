#!/bin/sh

module load prod_envir

ops=$COMROOT/rtofs/v2.3/
cd $ops
base=$HOME/noscrub/model_intercompare/rtofs_cice/
tag=20220920
end=`date +"%Y%m%d"`
end=`expr $end - 1`
end=`$HOME?bin/dtgfix3 $end`

while [ $tag -lt $end ]
do
  if [ ! -d ${base}/rtofs.$tag ] ; then
    find rtofs.$tag -name '*cice_inst' | cpio -pamdv $base
  else
    echo already have $tag
  fi

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
