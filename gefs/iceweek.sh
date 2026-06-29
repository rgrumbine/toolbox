#!/bin/sh
##ursa
#SBATCH -J iceweek6
#SBATCH -e iceweek6.err
#SBATCH -o iceweek6.out
#SBATCH -t 5:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=192g


source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/clim_data/replay/tmp

cd /home/Robert.Grumbine/clim_data/replay/thinned

#time python3 /home/Robert.Grumbine/clim_data/replay/tmp/iceweek.py
time python3 /home/Robert.Grumbine/clim_data/replay/tmp/universal.py 1 'ice' 'sigmoid'
