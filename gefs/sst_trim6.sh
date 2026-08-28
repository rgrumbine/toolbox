#!/bin/sh
##ursa
#SBATCH -J ssttrim6
#SBATCH -e ssttrim6.err
#SBATCH -o ssttrim6.out
#SBATCH -t 7:25:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=320g


source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

time python3 universal_trim6.py 1 'sst' 'linear'
report-mem
