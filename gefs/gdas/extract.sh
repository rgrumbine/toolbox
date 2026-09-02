#!/bin/sh

module load intel wgrib2
module load prod_envir
#set -x

#$COMROOT/gfs/v16.3/gdas.20260822/00/atmos

export COMROOT=/lfs/h2/emc/gfstemp/emc.global/comroot/retrov17_01_realtime/
#export COMROOT=$HOME/noscrub/gdas/

cd /u/robert.grumbine/rgdev/toolbox/gefs/gdas/

PDYm7=20260826
tag=$PDYm7
d=0
while [ $d -lt 7 ] 
#while [ $tag -le 20260830 ] 
do
  yy=`echo $tag | cut -c1-4`
  mm=`echo $tag | cut -c5-6`
  dd=`echo $tag | cut -c7-8`
  
  #PRS
  base=$COMROOT/gdas.$tag/00/analysis/atmos/

  if [ ! -f thinned/prs.${yy}${mm}${dd}.nc ] ; then
    wgrib2 $base/gdas.t00z.master.analysis.grib2 | grep -f prsget | wgrib2 -i $base/gdas.t00z.master.analysis.grib2 \
	    -new_grid gaussian 0:1536:0.234375 89.820709:768 a.grib2 
    wgrib2 a.grib2 -netcdf thinned/prs.${yy}${mm}${dd}.nc
    rm a.grib2
  fi
    
  #FLX
  base=$COMROOT/gdas.$tag/00/model/atmos/master/

  if [ ! -f thinned/flx.${yy}${mm}${dd}.nc ] ; then
    #grep -f flxget $base/gdas.t00z.sflux.f000.grib2.idx | wgrib2 -i $base/gdas.t00z.sflux.f000.grib2 \
    wgrib2 $base/gdas.t00z.sflux.f000.grib2 | grep -f flxget | wgrib2 -i $base/gdas.t00z.sflux.f000.grib2 \
	    -new_grid gaussian 0:1536:0.234375 89.820709:768 b.grib2

    wgrib2 b.grib2 -netcdf thinned/flx.${yy}${mm}${dd}.nc
    rm b.grib2
  fi

  d=`expr $d + 1`
  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done


# /lfs/h2/emc/gfstemp/emc.global/comroot/retrov17_01_realtime//gdas.20260831/00/model/atmos/master/gdas.t00z.master.f000.grib2
# /lfs/h2/emc/gfstemp/emc.global/comroot/retrov17_01_realtime//gdas.20260831/00/model/atmos/master/gdas.t00z.sflux.f000.grib2
