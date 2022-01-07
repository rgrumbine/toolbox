#!/bin/sh -l
#SBATCH -J test1
#SBATCH --account=nggps_emc
#  #SBATCH --clusters=c3
#SBATCH --clusters=es
#SBATCH --partition=rdtn
#  #SBATCH --qos=rdtn
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=1
#SBATCH -e alpha.err
#SBATCH -o alpha.out

echo hello
