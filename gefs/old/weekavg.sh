#!/bin/sh
##ursa
#SBATCH -J weekavg
#SBATCH -e weekavg.err
#SBATCH -o weekavg.out
#SBATCH -t 0:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH -N 1
#SBATCH --mem=8g

source $HOME/rg/env3.13/bin/activate

cd /home/Robert.Grumbine/clim_data/replay/thinned

time python3 /home/Robert.Grumbine/rgdev/toolbox/gefs/weekavg.py
