#!/bin/bash --login
#PBS -N tohpss
#PBS -o tohpss
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=1:00:00
#PBS -l select=1:ncpus=1

set -x

cd /u/robert.grumbine/noscrub/for_hpss

export base=/NCEPDEV/emc-marine/1year/Robert.Grumbine/

for f in cactus.fly.rgdef.tar
do
  hsi put $f : $base/$f
done

