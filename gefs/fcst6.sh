#!/bin/sh
##ursa
#SBATCH -J fcst6
#SBATCH -e fcst6.err
#SBATCH -o fcst6.out
#SBATCH -t 0:07:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=20g


source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

#time python3 forecast6.py ssttrim6.joblib 1
time python3 forecast6.py icetrim6.joblib 0
report-mem
