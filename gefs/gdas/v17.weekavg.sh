#!/bin/sh
##Wcoss2
#PBS -N gdasavg
#PBS -o gdasavg.out
#PBS -j oe
#PBS -A ICE-DEV
#PBS -q dev
#PBS -l walltime=0:05:00
#PBS -l select=1:ncpus=1
##ursa
##SBATCH -J weekavg2
##SBATCH -e weekavg2.err
##SBATCH -o weekavg2.out
##SBATCH -t 0:15:00
##SBATCH -q batch
##SBATCH -A marine-cpu
##SBATCH -N 1
##SBATCH --mem=8g

#ursa: 
#source $HOME/rg/env3.13/bin/activate
#cd $HOME/clim_data/replay/thinned

#wcoss2: 
source $HOME/rg/env3.13/bin/activate
cd $HOME/noscrub/thinned.v17
#==================================================================

#RG: make end date an argument
tag=${tag:-`date +"%Y%m%d"`}
tag=20261107
while [ $tag -ge 20261010 ]
do
yy=`echo $tag | cut -c1-4`
mm=`echo $tag | cut -c5-6`
dd=`echo $tag | cut -c7-8`

time python3 $HOME/rgdev/toolbox/gefs/gdas/v17.weekavg.py $yy $mm $dd

tag=`expr $tag - 1 `
tag=`$HOME/bin/dtgfix3 $tag`
done
