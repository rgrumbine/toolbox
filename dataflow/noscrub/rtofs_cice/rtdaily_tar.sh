#!/bin/sh

tag=20250301
while [ $tag -le 20250331 ]
do
  echo $tag
  if [ -d rtofs.$tag ] ; then
    tar cf ../rtofs.${tag}.tar rtofs.$tag
  fi

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
