#!/bin/sh

module load prod_envir/2.0.6

DCOMDEV=$DCOMROOT/../../dev/dcom
ls -l $DCOMDEV
#echo zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz

tag=20250715
cd $HOME/noscrub/satellites/viirs

echo $DCOMDEV/$tag

#while [ $tag -le `date +"%Y%m%d"` ]
end=`date +"%Y%m%d"`
end=`expr $end - 1`
end=`$HOME/bin/dtgfix3 $end`
set -x

while [ $tag -le $end ]
do
  echo working on $tag
  if [ ! -d $tag ] ; then
    mkdir -p $HOME/noscrub/satellites/viirs/$tag
    time cp -p ${DCOMDEV}/${tag}/seaice/pda/JRR* $HOME/noscrub/satellites/viirs/$tag
  fi
  tag=`expr $tag + 1`
  tag=`dtgfix3 $tag`
done
