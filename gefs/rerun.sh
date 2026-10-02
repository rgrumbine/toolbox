#!/bin/sh
##ursa
#SBATCH -J rerun
#SBATCH -e rerun.err
#SBATCH -o rerun.out
#SBATCH -t 26:55:00
##SBATCH -q batch
#SBATCH -q long
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=328g
##SBATCH --mem=128g


source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

#time python3 rerun.py 1 'sst' 'linear'
time python3 rerun.py 0 'ice' 'linear'
report-mem
