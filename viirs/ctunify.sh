#!/bin/sh

source ~/env3.12/bin/activate
export PYTHONPATH=$PYTHONPATH:$HOME/rgops/mmablib/py

export IMS=$HOME/noscrub/verification/nsidc_ims/
export NSST=$HOME/noscrub/nsst/
export NCEP=$HOME/noscrub/com/seaice_analysis/

#ims = nc.Dataset(sys.argv[1])
#fin = open(sys.argv[2],"r")
#ncep = pygrib.open(sys.argv[3])
#nsst = pygrib.open(sys.argv[4])

#export tag=20250701
#export j=182
export tag=20250101
export   j=001


while [ $tag -le $end ]
do
  export yy=`echo $tag | cut -c1-4`
  export d3=`echo $tag | cut -c6-8`
  if [ ! -d $d3 ] ; then
    mkdir $d3
  fi
  
  for inst in npp n21 j01
  #for inst in npp 
  do
    if [ -f fout.${tag}.${inst}.ims ] ; then
      time python3 ctunify.py  \
    	$HOME/noscrub/verification/nsidc_ims/${yy}/ims${yy}${j}_4km_v1.3.nc \
    	fout.${tag}.${inst}.ims \
    	$NCEP/seaice_analysis.$tag/seaice.t00z.5min.grb.grib2 \
    	$NSST/$tag/rtgssthr_grb_0.083.grib2 > ${inst}.$tag.out
      if [ ! -d $d3/$inst ] ; then
        mkdir -p $d3/$inst
      fi
      mv fout.${tag}.${inst}.ims $d3/$inst
      mv ${inst}.$tag.out fout.0? $d3/$inst
    fi
  done 

  j=`expr $j + 1`
  if [ $j -lt 100 ] ; then
    j=0$j
  fi
  if [ $j -lt 10 ] ; then
    j=0$j
  fi
  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
