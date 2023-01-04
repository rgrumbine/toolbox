#!/bin/sh

#set -xe

echo zzz entered nic_edge.sh

cd $HOME/rgdev/edges/
#Wcoss2:  
#RG: better to use prod_envir, but dev/dcom is issue
base=/lfs/h1/ops/dev/dcom/

tag=20221101

while [ $tag -le `date +"%Y%m%d"` ]
do
  if [ -f ${base}/${tag}/seaice/pda/nedge_20* ] ; then
    cp -p ${base}/${tag}/seaice/pda/nedge_20* .
  fi
  if [ -f ${base}/${tag}/seaice/pda/sedge_20* ] ; then
    cp -p ${base}/${tag}/seaice/pda/sedge_20* .
  fi

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done

echo zzz leaving nic_edge.sh
