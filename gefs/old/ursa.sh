#!/bin/sh
##ursa
#SBATCH -J univ
#SBATCH -e univ.err
#SBATCH -o univ.out
#SBATCH -t 0:19:00
#SBATCH -q batch
#SBATCH -A marine-cpu
##SBATCH -N 1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=192g


source $HOME/rg/env3.13/bin/activate

cd /home/Robert.Grumbine/clim_data/replay/tmp/common

time python3 universal.py 1 'ice' 'sigmoid'

time python3 universal.py 1 'sst' 'linear'
