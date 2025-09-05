#!/bin/bash
#####
#PBS -l select=1:ncpus=1
#PBS -l walltime=5:59:00
#PBS -N viirs
#PBS -q "dev"
#PBS -j oe
#PBS -A ICE-DEV
#  #PBS -R "rusage[mem=1024]"
#####

module load prod_envir/2.0.6

module load intel netcdf
source $HOME/env3.12/bin/activate
export PYTHONPATH=$PYTHONPATH:$HOME/rgops/mmablib/py

tag=20250102

while [ $tag -le 20250801 ]
do
  if [ -d $HOME/noscrub/satellites/viirs/$tag ] ; then
    for inst in j01 npp n21
    do
      if [ ! -f  fout1.${tag}.$inst ] ; then
        time python3 ct_composite.py $HOME/noscrub/satellites/viirs/$tag/JRR-IceConcentration_v3r3_${inst}_s${tag}*
        mv fout1 fout1.${tag}.$inst
        mv fout2 fout2.${tag}.$inst
      fi
    done
  fi

  tag=`expr $tag + 1`
  tag=`dtgfix3 $tag`
done
