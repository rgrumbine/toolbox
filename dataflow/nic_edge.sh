#!/bin/sh

cd $HOME/rgdev/edges/
#wcoss1: base=/gpfs/dell1/nco/ops/dcom/dev/
#Wcoss2:  
#base=/lfs/h1/ops/prod/dcom/

base=/lfs/h1/ops/dev/dcom/

tag=`date +"%Y%m%d"`
tag=20220814
#ls -l ${base}/${tag}/seaice/pda/?edge*
#exit
while [ $tag -le `date +"%Y%m%d"` ]
do
  cp -p ${base}/${tag}/seaice/pda/?edge_20* .
  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
