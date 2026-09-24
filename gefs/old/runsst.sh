#!/bin/sh
##ursa
#SBATCH -J sst
#SBATCH -e sst.err
#SBATCH -o sst.out
#SBATCH -t 5:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH -N 1
#SBATCH --mem=224g

source $HOME/rg/env3.13/bin/activate

cd /home/Robert.Grumbine/clim_data/replay/thinned

time python3 /home/Robert.Grumbine/clim_data/replay/tmp/sst.py > unet.outsst
