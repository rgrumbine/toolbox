#!/bin/sh
##ursa
#SBATCH -J sstweek6
#SBATCH -e sstweek6.err
#SBATCH -o sstweek6.out
#SBATCH -t 3:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128g


source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

#time python3 /home/Robert.Grumbine/clim_data/replay/tmp/sstweek.py
time python3 universal6.py 2 'sst' 'linear'
report-mem
