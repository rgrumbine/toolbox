#!/bin/sh

tag=20230711
while [ $tag -le 20230731 ]
do
  echo $tag
  if [ -d rtofs.$tag ] ; then
    tar cf ../rtofs.${tag}.tar rtofs.$tag
  fi

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
