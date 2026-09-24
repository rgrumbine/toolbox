#!/bin/sh
##ursa
#SBATCH -J icetrim2007
#SBATCH -e icetrim2007.err
#SBATCH -o icetrim2007.out
#SBATCH -t 23:55:00
##SBATCH -q batch
#SBATCH -q long
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=320g


source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

#time python3 universal_trim6.py 0 'ice' 'linear'
time python3 universal_trim2007.py 0 'ice' 'linear'
report-mem
