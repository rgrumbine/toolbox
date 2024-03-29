#!/bin/sh 
#set -xe
set -e
echo zzz entered gefs_clean.sh

tag=20230501
end=`date +"%Y%m%d"`
#end=20220609

cd $HOME/noscrub/gefs/

cyc=00
while [ $tag -le $end ]
do
  echo zzz working on $tag
  winddir=gefs.${tag}
  if [ -d $winddir -a \( -f winds.${tag}.tar \) ] ; then
    rm -rf gefs.$tag
  fi

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
echo zzz leaving gefs_clean.sh

