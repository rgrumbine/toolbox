#!/bin/sh
##ursa
#SBATCH -J fcst
#SBATCH -e fcst.err
#SBATCH -o fcst.out
#SBATCH -t 0:15:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=24g


source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

#time python3 forecast.py sstweek1.joblib 2
time python3 forecast.py ice12week1.joblib 1
report-mem
