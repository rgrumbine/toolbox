#!/bin/sh
##ursa
#SBATCH -J perm
#SBATCH -e perm.err
#SBATCH -o perm.out
#SBATCH -t 0:35:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=128g

source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs

cd $PYTHONPATH

time python3 permute52.py 0 'ice' 'linear'
report-mem
