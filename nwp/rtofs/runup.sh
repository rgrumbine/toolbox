#!/bin/sh
#SBATCH -J nwp_rtofs
#SBATCH -e nwp_rtofs.err
#SBATCH -o nwp_rtofs.out
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
export base=$indir

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
#End of the v2.4 archive: end=20220912
#tag=20241020
export tag=20240911

#reverse -- now to past
#end=20220401
export end=20240901

cd rtofs
while [ $tag -ge $end ]
do

  yy=`echo $tag | cut -c1-4`
  mm=`echo $tag | cut -c5-6`
  dd=`echo $tag | cut -c7-8`
  #if [ ! -f $OUTDIR/out.$tag ] ; then
    time python3 rtofs_2ds.py $yy $mm $dd > $OUTDIR/out.$tag
  #fi
  if [ -f nwp_${tag}_000.png ] ; then
    mv nwp_${tag}_*.png $OUTDIR
  fi  
  if [ -f path_${tag}_000.kml ] ; then
    mv path_${tag}_*.kml $OUTDIR
  fi

  tag=`expr $tag - 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
