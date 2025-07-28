#!/bin/sh

source ~/env3.12/bin/activate
export PYTHONPATH=$PYTHONPATH:$HOME/rgops/mmablib/py

module load intel netcdf imagemagick
if [ ! -f ims ] ; then
  make
fi

base=$HOME/noscrub/satellites/viirs
tag=20250101

while [ $tag -le 20250102 ]
do
  for inst in n21 j01 npp
  do
#1) Composite viirs data (only):
    time python3 viirs_conc.py $base/$tag/JRR*Conc*$inst* > initial_composite.$inst.$tag

#2) tag viirs_conc output with i,j of IMS grid:
    ./ims initial_composite.$inst.$tag > initial_composite.$inst.$tag.out 

  done

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done

#3) Learn what decision tree is best:
#for inst in npp n21 j01
#do
#  cat *${inst}*.out > allout.$inst
#done

#  unify.sh, unify.py
#  rerun.py
#
#(once decision tree is decided, this becomes #1)
#1) Filter the data from an instrument (npp, n21, j01) 
#  composite.sh
#  composite.py
# 
#(optional)
#4) Plot the text output (fout1, fout2):
#  biplot.py fout1.$tag fout2.$tag title markersize

#
#Robert Grumbine
#16 July 2025
