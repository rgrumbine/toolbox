#!/bin/sh
##ursa
#SBATCH -J evalv16
#SBATCH -e evalv16.err
#SBATCH -o evalv16.out
#SBATCH -t 2:40:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16g

# Robert Grumbine
# 30 October 2026

source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

time python3 eval_v16.py ice00v16_6.joblib 0
report-mem
