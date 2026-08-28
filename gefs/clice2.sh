#!/bin/sh
##ursa
#SBATCH -J iceclim2
#SBATCH -e iceclim2.err
#SBATCH -o iceclim2.out
#SBATCH -t 7:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --mem=320g


source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

time python3 universal2.py 1 'ice' 'linear'
report-mem
