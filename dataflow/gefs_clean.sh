#!/bin/sh 
#set -xe
set -e
echo entered gefs_clean.sh

tag=20221231
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
echo leaving gefs_clean.sh

