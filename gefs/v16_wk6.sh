#!/bin/sh
##ursa
#SBATCH -J ice6
#SBATCH -e ice6.err
#SBATCH -o ice6.out
#SBATCH -t 7:55:00
#SBATCH -A marine-cpu
##SBATCH -p u1-gh
##SBATCH -q gpuwf
#SBATCH -p u1-compute
#SBATCH -q batch
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=360g
##SBATCH --mem=128g

# Robert Grumbine
# 30 October 2026

source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

time python3 v16_wk6.py 0 'ice' 'linear'
report-mem
