#!/bin/sh
##ursa
#SBATCH -J unet3
#SBATCH -e unet.err7
#SBATCH -o unet.out7
#SBATCH -t 5:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH -N 1
#SBATCH --mem=224g

source $HOME/rg/env3.13/bin/activate

cd /home/Robert.Grumbine/clim_data/replay/thinned

#time python3 averager.py > avg.out

time python3 /home/Robert.Grumbine/clim_data/replay/tmp/multilayer_multitarget.py > unet.outg
