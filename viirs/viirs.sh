#!/bin/sh

module load prod_envir/2.0.6

DCOMDEV=$DCOMROOT/../../dev/dcom
ls -l $DCOMDEV
#echo zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz

tag=20250619

echo $DCOMDEV/$tag
ls -l ${DCOMDEV}/${tag}
echo zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
ls -l ${DCOMDEV}/${tag}/seaice/
echo zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
ls -l ${DCOMDEV}/${tag}/seaice/pda/JRR*
#exit

#while [ $tag -le `date +"%Y%m%d"` ]
while [ $tag -le 20250625 ]
do
  mkdir -p $HOME/noscrub/satellites/viirs/$tag
  time cp -p ${DCOMDEV}/${tag}/seaice/pda/JRR* $HOME/noscrub/satellites/viirs/$tag
  tag=`expr $tag + 1`
  tag=`dtgfix3 $tag`
done
