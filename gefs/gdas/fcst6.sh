#!/bin/sh
##Wcoss2
#PBS -N fcst
#PBS -o fcst.out
#PBS -j oe
#PBS -A ICE-DEV
#PBS -q dev
#PBS -l walltime=0:06:00
#PBS -l select=1:ncpus=1:mem=16GB
##ursa
#SBATCH -J fcst
#SBATCH -e fcst.err
#SBATCH -o fcst.out
#SBATCH -t 0:06:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=20g


source $HOME/rg/env3.13/bin/activate
#ursa
export PYTHONPATH=$HOME/rgdev/toolbox/gefs
#wcoss2
export PYTHONPATH=$HOME/rgdev/toolbox/gefs/


cd $PYTHONPATH/gdas
time python3 fcst6.py u6.ice.joblib 0
