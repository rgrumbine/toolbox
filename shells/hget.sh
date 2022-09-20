#!/bin/bash --login
#PBS -N heraget
#PBS -o heraget
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=6:00:00
#PBS -l select=1:ncpus=1

set -x

target=hera
if [ ! -d /u/robert.grumbine/noscrub/$target ] ; then
	mkdir -p /u/robert.grumbine/noscrub/$target
fi
cd /u/robert.grumbine/noscrub/$target

export base=/NCEPDEV/emc-marine/1year/Robert.Grumbine/
hsi mget $base/hera.*

