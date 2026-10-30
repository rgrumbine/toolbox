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
##SBATCH --mem=16g
##Wcoss2
#PBS -N fcst
#PBS -o fcst.out
#PBS -j oe
#PBS -A ICE-DEV
#PBS -q dev
#PBS -l walltime=0:09:00
#PBS -l select=1:ncpus=1:mem=16GB

# Robert Grumbine
# 30 October 2026

#ursa
#source $HOME/rg/env3.13/bin/activate
#export PYTHONPATH=$HOME/rgdev/toolbox/gefs
#wcoss2
source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=$HOME/rgdev/toolbox/gefs/


cd $PYTHONPATH/gdas
time python3 fcst52.py iceice52.joblib 0
report-mem
