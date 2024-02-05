#!/bin/sh
#
tag=20230101
base=$HOME/noscrub/filter/

while [ $tag -le 20230531 ]
do
  echo $tag
  ./seaice_totext ${base}/amsr2.${tag}/amsr2.$tag amsr2_${tag}.txt

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
