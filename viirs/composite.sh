#!/bin/sh

module load prod_envir/2.0.6


tag=20250627

while [ $tag -le 20250707 ]
do
  #time python3 composite.py $HOME/noscrub/satellites/viirs/$tag/JRR-IceConcentration_v3r3_npp_s${tag}*
  #time python3 composite.py $HOME/noscrub/satellites/viirs/$tag/JRR-IceConcentration_v3r3_n21_s${tag}*
  time python3 composite.py $HOME/noscrub/satellites/viirs/$tag/JRR-IceConcentration_v3r3_j01_s${tag}*
  mv fout1 fout1.$tag
  mv fout2 fout2.$tag

  tag=`expr $tag + 1`
  tag=`dtgfix3 $tag`
done
