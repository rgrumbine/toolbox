#!/bin/bash


base=$HOME/noscrub/filter/
cd $base

# for dumpjb (getting the bufr inputs)
source $HOME/rgdev/rg.analy/ecf/jobcards
export DCOMROOT=~/noscrub/satellites/prod/
export TMPDIR=/lfs/h2/emc/ptmp/wx21rg/dumpjb

module load bufr_dump
module load bufr
set +xe

tag=20240229
#tag=20230701
#while [ $tag -ge 20220601 ]
while [ $tag -ge 20240101 ]
do
  #echo checking $tag
  
# check filter archive:
  if [ ! -f txt/amsr2_$tag.txt.0 ] ; then
    if [ -f dirs/amsr2.$tag/amsr2.$tag ] ; then
      mv dirs/amsr2.$tag/amsr2.$tag bin/
    fi
  fi

# create the text files from bin:
  if [ ! -f txt/amsr2_${tag}.txt.0 -a -f ${base}/bin/amsr2.${tag} ] ; then
    ./seaice_totext ${base}/bin/amsr2.${tag} txt/amsr2_${tag}.txt
  fi

# bufr to bin
  if [ ! -f txt/amsr2_${tag}.txt.0 -a ! -f ${base}/bin/amsr2.${tag} -a -f bufr/amsr2.$tag ] ; then
    ln -s bufr/amsr2.$tag fort.11
    time ./seaice_amsrbufr 
    mv fort.52 bin/amsr2.$tag
    rm fort.11 fort.51
  fi

# get bufr -- dumpjb from my archive:
  if [ ! -f txt/amsr2_${tag}.txt.0 -a ! -f ${base}/bin/amsr2.${tag} -a ! -f bufr/amsr2.$tag ] ; then
#    /apps/ops/prod/nco/intel/19.1.3.304/bufr_dump.v1.1.2/install/ush/dumpjb ${tag}00 12 amsr2
    echo zzz mv amsr2.ibm bufr/amsr2.${tag}
  fi

  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
