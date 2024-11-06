#!/bin/sh
#SBATCH -J nwp9_cafs
#SBATCH -e nwp9_cafs.err
#SBATCH -o nwp9_cafs.out
#SBATCH -t 7:55:00
#  #SBATCH -t 0:25:00
#SBATCH -q batch
# change this to your #SBATCH -A marine-cpu
#SBATCH -N 1
#SBATCH --mail-type FAIL
#SBATCH --mail-user USER@system

#------------------------------------------------------

# Path to cafs output (used internally to program -- change this)
export base=/home/Robert.Grumbine/clim_data/cafs/

# location of python and support -- change this to your location
cd /home/Robert.Grumbine/rgdev/toolbox/nwp/cafs

# Change to anything of convenience
export MPLCONFIGDIR=$HOME/rgexpt/
export OUTDIR=$HOME/rgdev/cafs_nwp

#------------------------------------------------------

# These must be more or less exactly this:
source /home/Robert.Grumbine/rgref/env3.12/bin/activate
export PYTHONPATH=$PYTHONPATH:/home/Robert.Grumbine/rgdev/toolbox/nwp

#------------------------------------------------------
tag=`date +"%Y%m%d"`
tag=`expr $tag - 1`
tag=`$HOME/bin/dtgfix3 $tag`
#debug: tag=20241022
tag=20241028

#reverse -- now to past
end=20241104
#debug: end=20241011

while [ $tag -ge $end ]
do
  echo working on $tag

  yy=`echo $tag | cut -c1-4`
  mm=`echo $tag | cut -c5-6`
  dd=`echo $tag | cut -c7-8`
  #if [ ! -f $OUTDIR/${yy}/out.$tag -o ! -f $OUTDIR/${yy}/nwp_${tag}_240.png \
  #       -o ! -f $OUTDIR/${yy}/path_${tag}_240.kml ] ; then
    time python3 new_cafs.py $yy $mm $dd > $OUTDIR/${yy}/out.$tag
  #fi
  if [ -f nwp_${tag}_240.png ] ; then
    mv nwp_${tag}_*.png $OUTDIR/${yy}
  fi  
  if [ -f path_${tag}_240.kml ] ; then
    mv path_${tag}_*.kml $OUTDIR/${yy}
  fi  

  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
