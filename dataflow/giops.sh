#!/bin/sh

mm=09
for d in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
do
  tag=2022${mm}$d
  if [ ! -d giops.$tag ] ; then
    base=/lfs/h1/ops/dev/dcom/$tag/wgrbbul/cmc_giops
    if [ -d $base ] ; then
      time cp -rp $base giops.$tag
    else
      echo no directory for $tag
    fi
  fi
done
