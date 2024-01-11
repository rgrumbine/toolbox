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
#if [ ! -d /u/robert.grumbine/noscrub/satellites/$target ] ; then
#	mkdir -p /u/robert.grumbine/noscrub/satellites/$target
#fi
cd /u/robert.grumbine/noscrub/$target

export base=/NCEPDEV/emc-marine/5year/Robert.Grumbine/

for f in sats.1999.tar sats.2000.tar sats.2002.tar sats.2003.tar sats.2004.tar sats.2001.tar 
do
  hsi put $base/$target/$f
done

