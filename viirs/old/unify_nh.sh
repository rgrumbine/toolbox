#!/bin/sh

source ~/env3.12/bin/activate
export PYTHONPATH=$PYTHONPATH:$HOME/rgops/mmablib/py


export IMS=$HOME/noscrub/verification/nsidc_ims/
export NSST=$HOME/noscrub/nsst/
export NCEP=$HOME/noscrub/com/seaice_analysis/

#export tag=20250714
#export j=195
export tag=20250627
export   j=178

while [ $tag -le 20250714 ]
do
  export yy=`echo $tag | cut -c1-4`
  export d3=`echo $tag | cut -c6-8`
  
  for inst in npp n21 j01
  #for inst in npp 
  do
    time python3 unify.py  \
  	$HOME/noscrub/verification/nsidc_ims/${yy}/ims${yy}${j}_4km_v1.3.nc \
  	$d3/initial_composite.${inst}.${tag}.out \
  	$NCEP/seaice_analysis.$tag/seaice.t00z.5min.grb.grib2 \
  	$NSST/$tag/rtgssthr_grb_0.083.grib2 > ${inst}.$tag.out
    mkdir -p $d3/$inst
    mv ${inst}.$tag.out fout.0? $d3/$inst
  done 

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
  j=`expr $j + 1`
done

