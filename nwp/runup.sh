#!/bin/sh

# enable sbatch submission

#These can be anything of convenience
export MPLCONFIGDIR=$HOME/rgexpt/
export OUTDIR=$HOME/rgdev/cafs_nwp

# This must be more or less exactly this:
source /home/Robert.Grumbine/rgref/env3.12/bin/activate

# Path to cafs is currently hard-wired in the python program (boo!) RG


#tag=20220401
tag=20241001

end=`date +"%Y%m%d"`
#debug: end=20241011

while [ $tag -le $end ]
do

  yy=`echo $tag | cut -c1-4`
  mm=`echo $tag | cut -c5-6`
  dd=`echo $tag | cut -c7-8`
  if [ ! -f $HOME/rgdev/cafs_nwp/out.$tag ] ; then
    time python3 oper_cafs.py $yy $mm $dd > $OUTDIR/out.$tag
  fi
  if [ -f nwp_${tag}_00.png ] ; then
    mv nwp_${tag}_00.png $OUTDIR
  fi  
  if [ -f path_${tag}_00.kml ] ; then
    mv path_${tag}_00.kml $OUTDIR
  fi  

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
