#!/bin/sh
##ursa
#SBATCH -J ice52
#SBATCH -e ice52.err
#SBATCH -o ice52.out
##SBATCH -t 26:55:00
##SBATCH -q long
#SBATCH -t 6:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=128
#SBATCH --mem=360g
##SBATCH --mem=128g


source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

time python3 ice52.py 0 'ice' 'linear'
report-mem
