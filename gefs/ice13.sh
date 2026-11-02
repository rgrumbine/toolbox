#!/bin/sh
##ursa
#SBATCH -J ice13
#SBATCH -e ice13.err
#SBATCH -o ice13.out
#SBATCH -t 26:55:00
##SBATCH -q batch
#SBATCH -q long
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
##SBATCH --mem=328g
#SBATCH --mem=128g

# Robert Grumbine
# 29 September 2026

source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

time python3 ice13.py 0 'ice' 'linear'
report-mem
