#!/bin/sh
#
tag=20250102
base=$HOME/noscrub/com/seaice_analysis/

while [ $tag -le 20250614 ]
do
  echo $tag
  if [ ! -f $base/seaice_analysis.${tag}/amsr2_${tag}.txt.1 ] ; then
    time ./seaice_totext ${base}/seaice_analysis.${tag}/amsr2.bufr $base/seaice_analysis.${tag}/amsr2_${tag}.txt
  fi

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
