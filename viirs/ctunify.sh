#!/bin/bash
#####
#PBS -l select=1:ncpus=1
#PBS -l walltime=5:59:00
#PBS -N ctunify8
#PBS -q "dev"
#PBS -j oe
#PBS -A ICE-DEV
#  #PBS -R "rusage[mem=1024]"
#####

source ~/env3.12/bin/activate
export PYTHONPATH=$PYTHONPATH:$HOME/rgops/mmablib/py
export EXDIR=$HOME/rgdev/toolbox/viirs

export IMS=$HOME/noscrub/verification/nsidc_ims/
export NSST=$HOME/noscrub/nsst/
export NCEP=$HOME/noscrub/com/seaice_analysis/

#ims = nc.Dataset(sys.argv[1])
#fin = open(sys.argv[2],"r")
#ncep = pygrib.open(sys.argv[3])
#nsst = pygrib.open(sys.argv[4])

#export tag=20250701
#export j=182
export tag=20250801
export   j=001
export end=20250905

pid=$$
export RUN=/lfs/h2/emc/ptmp/wx21rg/ctunify.$pid
mkdir -p $RUN
cd $RUN

export COMOUT=$HOME/noscrub/viirsout/

while [ $tag -le $end ]
do
  export yy=`echo $tag | cut -c1-4`
  export d4=`echo $tag | cut -c5-8`
  if [ ! -d $COMOUT/$d4 ] ; then
    mkdir $COMOUT/$d4
  fi
  
  for inst in npp n21 j01
  do
    if [ -f $COMOUT/fout.${tag}.${inst} ] ; then
      echo working on $tag $inst
      if [ ! -f $COMOUT/fout.${tag}.${inst}.ims ] ; then
	$EXDIR/ims $COMOUT/fout.${tag}.${inst} > $COMOUT/fout.${tag}.${inst}.ims
      fi
      if [ ! -f $d4/$inst/${inst}.$tag.out ] ; then
        time python3 $EXDIR/ctunify.py  \
      	$HOME/noscrub/verification/nsidc_ims/${yy}/ims${yy}${j}_4km_v1.3.nc \
      	$COMOUT/fout.${tag}.${inst}.ims \
      	$NCEP/seaice_analysis.$tag/seaice.t00z.5min.grb.grib2 \
      	$NSST/$tag/rtgssthr_grb_0.083.grib2 > ${inst}.$tag.out

        if [ ! -d $COMOUT/$d4/$inst ] ; then
          mkdir -p $COMOUT/$d4/$inst
        fi
        mv ${inst}.$tag.out fout.0? $COMOUT/$d4/$inst

      fi
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
