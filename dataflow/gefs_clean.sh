#!/bin/sh --login
#set -xe
set -e

tag=20220501
end=`date +"%Y%m%d"`
#end=20220609

cd $HOME/noscrub/gefs/

cyc=00
while [ $tag -le $end ]
do
  echo working on $tag
  winddir=gefs.${tag}
  if [ -d $winddir -a \( -f winds.${tag}.tar \) ] ; then
    rm -rf gefs.$tag
  fi

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
