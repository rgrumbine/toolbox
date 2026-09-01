#!/bin/sh
##ursa
#SBATCH -J eval6
#SBATCH -e eval6.err
#SBATCH -o eval6.out
#SBATCH -t 6:40:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=20g


source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

#time python3 eval6.py ssttrim6.joblib 1
time python3 eval6.py icetrim6.joblib 0
report-mem
