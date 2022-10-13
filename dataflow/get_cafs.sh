#!/bin/sh

models=$HOME/noscrub/model_intercompare/
if [ ! -d $models/cafs ] ; then
	mkdir $models/cafs
fi
cd $models/cafs


base=`pwd`
tag=20220101
while [ $tag -lt `date +"%Y%m%d"` ]
do

  if [ ! -d $tag ] ; then

    mkdir $tag
    cd $tag
  
    YYYY=`echo $tag | cut -c1-4`
    MM=`echo $tag | cut -c5-6`
    DD=`echo $tag | cut -c7-8`
  
    wget -q ftp://ftp1.esrl.noaa.gov/RASM-ESRL/ModelOutput/*$YYYY-$MM-$DD*

  fi
  cd $base
  tag=`expr $tag + 1`
  tag=`/u/robert.grumbine/bin/dtgfix3 $tag`
done
exit

total 573116
-r--r--r-- 1 Robert.Grumbine couple  81764774 May 30 15:32 RASM-ESRL_4NIC_2022-05-30.tar.gz
-r--r--r-- 1 Robert.Grumbine couple  51857228 May 30 15:35 RASM-ESRL_4SIPN_2022-05-30.tar.gz
-r--r--r-- 1 Robert.Grumbine couple 349235272 May 30 14:31 REB2.2022-05-30.nc
-r--r--r-- 1 Robert.Grumbine couple 104002756 May 30 15:26 REB2_plots.2022-05-30.tar.gz
