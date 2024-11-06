#!/bin/sh

tag=20230103
while [ $tag -le 20230331 ]
do
  d=`echo $tag | cut -c5-8`
  if [ ! -d $d ] ; then
    mkdir $d
  fi
  time python3 quick_thin.py orig/matched_$tag.txt > $d/out.txt 
  mv f00 f01 f10 f11 $d

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
