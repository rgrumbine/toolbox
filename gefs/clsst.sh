#!/bin/sh
##ursa
#SBATCH -J sstclim
#SBATCH -e sstclim.err
#SBATCH -o sstclim.out
#SBATCH -t 0:40:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128g


source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

time python3 climate6.py 1 'sst' 'linear'
report-mem
