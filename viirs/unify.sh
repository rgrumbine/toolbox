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

export tag=20250714
export j=195
export inst=npp

#for f in $IMS/$tag/wgrbbul/imssnow96.grb.grib2 allout.$inst \
#	$NSST/$tag/rtgssthr_grb_0.083.grib2 \
#	$NCEP/seaice_analysis.$tag/seaice.t00z.5min.grb.grib2
#do
#  if [ ! -f $f ] ; then
#    echo missing $f
#  else
#    echo have file
#  fi
#done
#
#exit

export yy=`echo $tag | cut -c1-4`
python3 unify.py  \
	$HOME/noscrub/verification/nsidc_ims/${yy}/ims${yy}${j}_4km_v1.3.nc \
	allout.$inst \
	$NCEP/seaice_analysis.$tag/seaice.t00z.5min.grb.grib2 \
	$NSST/$tag/rtgssthr_grb_0.083.grib2 

