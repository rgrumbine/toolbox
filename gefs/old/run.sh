#!/bin/sh
##ursa
#SBATCH -J unet
#SBATCH -e unet.err4
#SBATCH -o unet.out4
#SBATCH -t 1:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH -N 1
#SBATCH --mem=192g
##Wcoss2
##PBS -N driftup
##PBS -o driftup
##PBS -j oe
##PBS -A ICE-DEV
##PBS -q dev
##PBS -l walltime=6:00:00
##PBS -l select=1:ncpus=1


source $HOME/rg/env3.13/bin/activate

cd /home/Robert.Grumbine/clim_data/replay/thinned

#time python3 averager.py > avg.out

time python3 /home/Robert.Grumbine/clim_data/replay/tmp/multilayer_multitarget.py > unet.out
