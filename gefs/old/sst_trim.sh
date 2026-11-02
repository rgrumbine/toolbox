#!/bin/sh
##ursa
#SBATCH -J ssttrim
#SBATCH -e ssttrim.err
#SBATCH -o ssttrim.out
#SBATCH -t 7:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --mem=288g


source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

time python3 universal_trim.py 1 'sst' 'linear'
report-mem
