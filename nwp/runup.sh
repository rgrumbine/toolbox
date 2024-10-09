#!/bin/sh

export MPLCONFIGDIR=$HOME/rgexpt/

tag=20220401
while [ $tag -le `date +"%Y%m%d"` ]
do

  yy=`echo $tag | cut -c1-4`
  mm=`echo $tag | cut -c5-6`
  dd=`echo $tag | cut -c7-8`
  if [ ! -f $HOME/rgdev/cafs_nwp/out.$tag ] ; then
    time python3 oper_cafs.py $yy $mm $dd > $HOME/rgdev/cafs_nwp/out.$tag
  fi

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
