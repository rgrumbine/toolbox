#!/bin/bash --login
#PBS -N putsat
#PBS -o putsat
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=6:00:00
#PBS -l select=1:ncpus=1

set -x

target=satellites
cd /u/robert.grumbine/noscrub/$target

export base=/NCEPDEV/emc-marine/5year/Robert.Grumbine/

for f in  sats.202206.tar sats.202207.tar sats.202208.tar sats.202209.tar
do
  hsi put $f : $base/$target/$f
done

