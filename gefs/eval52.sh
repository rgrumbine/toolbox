#!/bin/sh
##ursa
#SBATCH -J eval52
#SBATCH -e eval52.err
#SBATCH -o eval52.out
#SBATCH -t 2:40:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=32g

# Robert Grumbine
# 30 October 2026

source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

time python3 eval52.py iceice52.joblib 0
report-mem
