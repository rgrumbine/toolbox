#!/bin/sh
##ursa
##SBATCH -J fcst52
##SBATCH -e fcst52.err
##SBATCH -o fcst52.out
##SBATCH -t 0:06:00
##SBATCH -q batch
##SBATCH -A marine-cpu
##SBATCH --nodes=1
##SBATCH --ntasks-per-node=1
##SBATCH --cpus-per-task=1
##SBATCH --mem=16g
##Wcoss2
#PBS -N fcst52
#PBS -o fcst52.out
#PBS -j oe
#PBS -A ICE-DEV
#PBS -q dev
#PBS -l walltime=5:09:00
#PBS -l select=1:ncpus=1:mem=16GB

# Robert Grumbine
# 30 October 2026

#ursa
#source $HOME/rg/env3.13/bin/activate
#export PYTHONPATH=$HOME/rgdev/toolbox/gefs
#wcoss2
source $HOME/rg/env3.13/bin/activate
export EXDIR=$HOME/rgdev/toolbox/gefs/gdas
export PYTHONPATH=$HOME/rgdev/toolbox/gefs/


cd $EXDIR

tag=${tag:-`date +"%Y%m%d"`}
#tag=20261105
#while [ $tag -ge 20260708 ]
#do
yy=`echo $tag | cut -c1-4`
mm=`echo $tag | cut -c5-6`
dd=`echo $tag | cut -c7-8`

time python3 $EXDIR/v17.fcst52.py iceice52.joblib 0 $yy $mm $dd
#ursa: report-mem
mkdir -p ~/noscrub/gefs.sample/v17.fcst.$tag
mv fcst_*.nc ~/noscrub/gefs.sample/v17.fcst.$tag

#tag=`expr $tag - 1`
#tag=`$HOME/bin/dtgfix3 $tag`
#done
