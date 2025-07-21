#!/bin/sh

source ~/env3.12/bin/activate
export PYTHONPATH=$PYTHONPATH:$HOME/rgops/mmablib/py


export IMS=$HOME/noscrub/verification/nsidc_ims/
export NSST=$HOME/noscrub/nsst/
export NCEP=$HOME/noscrub/com/seaice_analysis/

#fin = open(sys.argv[1],"r")
#ncep = pygrib.open(sys.argv[2])
#nsst = pygrib.open(sys.argv[3])

#export tag=20250714
#export j=195

export tag=20250707
export   j=182
while [ $tag -le 20250708 ]
do
  
  export yy=`echo $tag | cut -c1-4`
  export d3=`echo $tag | cut -c6-8`
  
  for inst in npp n21 j01
  do
    time python3 unify_aa.py  \
  	$d3/initial_composite.$inst.$tag \
  	$NCEP/seaice_analysis.$tag/seaice.t00z.5min.grb.grib2 \
  	$NSST/$tag/rtgssthr_grb_0.083.grib2 > ${inst}.$tag.out
    mkdir -p aa/$d3/$inst
    mv ${inst}.$tag.out fout.0? aa/$d3/$inst
  done 

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
  j=`expr $j + 1`

done 
