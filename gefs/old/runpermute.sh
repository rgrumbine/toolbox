#!/bin/sh
##ursa
#SBATCH -J permute6
#SBATCH -e permute6.err
#SBATCH -o permute6.out
#SBATCH -t 1:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
##SBATCH -N 1
#SBATCH --mem=96g

source $HOME/rg/env3.13/bin/activate

cd /home/Robert.Grumbine/clim_data/replay/thinned

time python3 /home/Robert.Grumbine/clim_data/replay/tmp/multi_permute.py > unet.outpermute6
