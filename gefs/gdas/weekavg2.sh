#!/bin/sh
##Wcoss2
#PBS -N gdasavg
#PBS -o gdasavg.out
#PBS -j oe
#PBS -A ICE-DEV
#PBS -q dev
#PBS -l walltime=0:40:00
#PBS -l select=1:ncpus=1
##ursa
#SBATCH -J weekavg2
#SBATCH -e weekavg2.err
#SBATCH -o weekavg2.out
#SBATCH -t 0:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH -N 1
#SBATCH --mem=8g

#ursa: source $HOME/rg/env3.13/bin/activate
#ursa: cd $HOME/clim_data/replay/thinned

#wcoss2: 
source $HOME/env3.12/bin/activate
cd $HOME/noscrub/thinned


time python3 $HOME/rgdev/toolbox/gefs/gdas/weekavg2.py
