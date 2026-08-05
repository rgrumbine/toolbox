#!/bin/sh
##ursa
#SBATCH -J sstclim2
#SBATCH -e sstclim2.err
#SBATCH -o sstclim2.out
#SBATCH -t 7:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=192g


source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

time python3 universal1.py 2 'sst' 'linear'
report-mem
