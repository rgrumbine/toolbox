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

# Path to model output:
export indir=/home/Robert.Grumbine/clim_data/rtofs/

# location of python and support
export exdir=/home/Robert.Grumbine/rgdev/toolbox/nwp
cd $exdir

# This must be more or less exactly this:
source /home/Robert.Grumbine/rgref/env3.12/bin/activate
export PYTHONPATH=$PYTHONPATH:/home/Robert.Grumbine/rgdev/toolbox/nwp/

#These can be anything of convenience
export MPLCONFIGDIR=$HOME/rgexpt/
export OUTDIR=$HOME/rgdev/rtofs_nwp

#------------------------------------------------------
#tag=20220401
tag=20241020

#reverse -- now to past
#end=`date +"%Y%m%d"`
end=20220401

cd rtofs
while [ $tag -ge $end ]
do

  yy=`echo $tag | cut -c1-4`
  mm=`echo $tag | cut -c5-6`
  dd=`echo $tag | cut -c7-8`
  if [ ! -f $OUTDIR/out.$tag ] ; then
    time python3 rtofs.py $yy $mm $dd > $OUTDIR/out.$tag
  fi
  if [ -f nwp_${tag}_6.png ] ; then
    mv nwp_${tag}_*.png $OUTDIR
  fi  
  if [ -f path_${tag}_6.kml ] ; then
    mv path_${tag}_*.kml $OUTDIR
  fi

  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
