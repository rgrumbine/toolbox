#!/bin/bash
#####
#PBS -l select=1:ncpus=1
#PBS -l walltime=15:59:00
#PBS -N viirs7.comp
#PBS -q "dev"
#PBS -j oe
#PBS -A ICE-DEV
#  #PBS -R "rusage[mem=1024]"
#####

module load prod_envir/2.0.6

module load intel netcdf
source $HOME/env3.12/bin/activate
export PYTHONPATH=$PYTHONPATH:$HOME/rgops/mmablib/py

COMOUT=$HOME/noscrub/viirsout/
EXDIR=$HOME/rgdev/toolbox/viirs
pid=$$
mkdir -p /lfs/h2/emc/ptmp/wx21rg/viirs.$pid
cd       /lfs/h2/emc/ptmp/wx21rg/viirs.$pid

tag=20250101

while [ $tag -le 20250905 ]
do
  if [ -d $HOME/noscrub/satellites/viirs/$tag ] ; then
    echo checking $tag
    for inst in j01 npp n21
    do
      if [ ! -f  $COMOUT/fout.${tag}.$inst ] ; then
        time python3 $EXDIR/ct_composite.py $HOME/noscrub/satellites/viirs/$tag/JRR-IceConcentration_v3r3_${inst}_s${tag}*
	$EXDIR/ims fout > fout.${tag}.${inst}.ims
        mv fout $COMOUT/fout.${tag}.$inst
	mv fout.${tag}.${inst}.ims $COMOUT
      fi
    done
  else
    echo no viirs directory for $tag
  fi

  tag=`expr $tag + 1`
  tag=`dtgfix3 $tag`
done
