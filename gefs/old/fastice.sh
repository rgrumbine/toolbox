#!/bin/sh
##ursa
#SBATCH -J fast9
#SBATCH -e fast9.err
#SBATCH -o fast9.out
#SBATCH -t 1:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
##SBATCH -N 1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=80g

source $HOME/rg/env3.13/bin/activate

cd /home/Robert.Grumbine/clim_data/replay/thinned

time python3 /home/Robert.Grumbine/clim_data/replay/tmp/fast.py > unet.fast80gb.b16cpu.10gen.usage.2
