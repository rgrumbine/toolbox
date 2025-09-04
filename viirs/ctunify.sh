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
#export tag=20250629
#export   j=180
export tag=20250103
export   j=003

export yy=`echo $tag | cut -c1-4`
export d3=`echo $tag | cut -c6-8`

for inst in npp n21 j01
#for inst in npp 
do
  time python3 ctunify.py  \
	$HOME/noscrub/verification/nsidc_ims/${yy}/ims${yy}${j}_4km_v1.3.nc \
	initial_composite.${inst}.${tag}.out \
	$NCEP/seaice_analysis.$tag/seaice.t00z.5min.grb.grib2 \
	$NSST/$tag/rtgssthr_grb_0.083.grib2 > ${inst}.$tag.out
  mkdir -p $inst
  mv ${inst}.$tag.out fout.0? $d3/$inst
done 

