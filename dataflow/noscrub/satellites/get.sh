#!/bin/bash --login
#PBS -N getsat
#PBS -o getsat
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=6:00:00
#PBS -l select=1:ncpus=1

set -x

target=satellites
cd /u/robert.grumbine/noscrub/$target

export base=/NCEPDEV/emc-marine/5year/Robert.Grumbine/

for yy in 2020
do
for mm in 12
do
  hsi get $base/$target/satellites.${yy}${mm}.tar
done
done

for yy in 2021
do 
  for mm in 01 02 03
  do
    hsi get $base/sats.${yy}${mm}.tar
  done
done
