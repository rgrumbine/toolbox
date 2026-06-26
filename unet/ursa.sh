#!/bin/sh
##ursa
#SBATCH -J nsidc
#SBATCH -e nsidc.err
#SBATCH -o nsidc.out
#SBATCH -t 5:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
##SBATCH -N 1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=12
#SBATCH --mem=24g


source $HOME/rg/env3.13/bin/activate

cd /home/Robert.Grumbine/rgdev/toolbox/unet

#time python3 /home/Robert.Grumbine/rgdev/toolbox/unet/loop3.py
time python3 /home/Robert.Grumbine/rgdev/toolbox/unet/loop3sh.py
