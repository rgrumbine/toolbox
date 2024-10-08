#!/bin/sh

tag=20220401
while [ $tag -le 20241008 ]
do

  yy=`echo $tag | cut -c1-4`
  mm=`echo $tag | cut -c5-6`
  dd=`echo $tag | cut -c7-8`
  time python3 oper_cafs.py $yy $mm $dd > out.$tag

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
