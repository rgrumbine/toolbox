#!/bin/sh
##ursa
#SBATCH -J avg
#SBATCH -e avg.err2
#SBATCH -o avg.out2
#SBATCH -t 0:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH -N 1
#SBATCH --mem=8g
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

time python3 /home/Robert.Grumbine/clim_data/replay/tmp/averager.py > avg.out
