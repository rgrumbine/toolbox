#!/bin/sh
##ursa
#SBATCH -J iceweek
#SBATCH -e iceweek.err
#SBATCH -o iceweek.out
#SBATCH -t 5:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=192g


source $HOME/rg/env3.13/bin/activate
export PYTHONPATH=/home/Robert.Grumbine/rgdev/toolbox/gefs/

cd $PYTHONPATH

#time python3 /home/Robert.Grumbine/clim_data/replay/tmp/iceweek.py
time python3 universal1.py 1 'ice' 'sigmoid'
