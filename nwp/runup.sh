#!/bin/sh
#SBATCH -J nwp_cafs
#SBATCH -e nwp_cafs.err
#SBATCH -o nwp_cafs.out
#SBATCH -t 7:55:00
#  #SBATCH -t 0:25:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#  #SBATCH -A fv3-cpu
#SBATCH -N 1
#SBATCH --mail-type FAIL
#SBATCH --mail-user USER@system

# RG: enable sbatch submission

# RG: location of python support
cd /home/Robert.Grumbine/rgdev/toolbox/nwp

# This must be more or less exactly this:
source /home/Robert.Grumbine/rgref/env3.12/bin/activate

# Path to cafs is currently hard-wired in the python program (boo!) RG
export base=/home/Robert.Grumbine/clim_data/cafs/

#These can be anything of convenience
export MPLCONFIGDIR=$HOME/rgexpt/
export OUTDIR=$HOME/rgdev/cafs_nwp

#------------------------------------------------------
tag=20220401
#debug: tag=20241001

end=`date +"%Y%m%d"`
#debug: end=20241011

while [ $tag -le $end ]
do

  yy=`echo $tag | cut -c1-4`
  mm=`echo $tag | cut -c5-6`
  dd=`echo $tag | cut -c7-8`
  #if [ ! -f $HOME/rgdev/cafs_nwp/out.$tag ] ; then
    time python3 new_cafs.py $yy $mm $dd > $OUTDIR/out.$tag
  #fi
  if [ -f nwp_${tag}_00.png ] ; then
    mv nwp_${tag}_00.png $OUTDIR
  fi  
  if [ -f path_${tag}_00.kml ] ; then
    mv path_${tag}_00.kml $OUTDIR
  fi  

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
