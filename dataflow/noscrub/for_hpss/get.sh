#!/bin/bash --login
#PBS -N gethpss
#PBS -o gethpss
#PBS -j oe
#PBS -A XFER-DEV
#PBS -q dev_transfer
#PBS -l walltime=6:00:00
#PBS -l select=1:ncpus=1

set -x

cd /u/robert.grumbine/noscrub/for_hpss

#export base=/NCEPDEV/emc-marine/5year/Robert.Grumbine/
#export base=/NCEPDEV/emc-climate/1year/Robert.Grumbine/
export base=/NCEPDEV/emc-marine/1year/Robert.Grumbine/

hsi mget $base/rtofs*.tar

#for f in gefs.202003.tar gefs.202004.tar gefs.202005.tar
#do
#  hsi get $base/gefs/$f
#done

exit
