#!/bin/sh
##ursa
#SBATCH -J eval13
#SBATCH -e eval13.err
#SBATCH -o eval13.out
#SBATCH -t 0:40:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16g

# Robert Grumbine
# 29 September 2026

source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

time python3 eval13.py ice112ice13.joblib 0
report-mem
