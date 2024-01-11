#!/bin/bash 
#PBS -N tohpss
#PBS -o tohpss
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=6:00:00
#PBS -l select=1:ncpus=1

set -x

module list

cd /u/robert.grumbine/noscrub/for_hpss

export base=/NCEPDEV/emc-marine/5year/Robert.Grumbine/

for f in *.tar *.tgz *.cpio
do
  hsi put $f : $base/$f
done

exit
