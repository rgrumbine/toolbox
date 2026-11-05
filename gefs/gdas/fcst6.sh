#!/bin/sh
##ursa
##SBATCH -J fcst
##SBATCH -e fcst.err
##SBATCH -o fcst.out
##SBATCH -t 0:06:00
##SBATCH -q batch
##SBATCH -A marine-cpu
##SBATCH --nodes=1
##SBATCH --ntasks-per-node=1
##SBATCH --cpus-per-task=1
##SBATCH --mem=20g
##Wcoss2
#PBS -N fcst
#PBS -o fcst.out
#PBS -j oe
#PBS -A ICE-DEV
#PBS -q dev
#PBS -l walltime=0:09:00
#PBS -l select=1:ncpus=1:mem=16GB


source $HOME/rg/env3.13/bin/activate
#ursa
export PYTHONPATH=$HOME/rgdev/toolbox/gefs
#wcoss2
export PYTHONPATH=$HOME/rgdev/toolbox/gefs/
export EXDIR=$PYTHONPATH/gdas


tag=${tag:-`date +"%Y%m%d"`}

# need this for links to climate, thinned directories, and the model
cd $EXDIR
time python3 v16fcst.py icev16_6.joblib 0
mkdir ~/noscrub/gefs.sample/fcst.$tag
mv fcst_*.nc ~/noscrub/gefs.sample/fcst.$tag

