#!/bin/sh --login
#SBATCH -J yopp3a
#SBATCH -e yopp3a.err
#SBATCH -o yopp3a.out
#SBATCH -t 7:55:00
#  #SBATCH -t 0:29:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#  #SBATCH -A fv3-cpu
#SBATCH -N 1
#SBATCH --mail-type FAIL
#SBATCH --mail-user USER@system

#-------------------------- Reference -------------------------------
#Arctic SOP1:
start=20180201
end=20180331

#Arctic SOP2:
start=20180701
end=20180930

#Antarctic SOP1:
start=20181116
end=20190215

#Mosaic:
start=20191001
end=20201012

#Antarctic SOP2:
start=20220415
end=20220831

#-------------------------- END Reference -------------------------------
module load hpss/hpss
module load hpc/1.2.0 intel/2022.1.2 hpc-intel/2022.1.2
module load impi/2022.1.2 hpc-impi/2022.1.2
module load hdf5/1.10.6 wgrib2/2.0.8 netcdf/4.7.0
. python_load
module list

export YDIR=$HOME/rgdev/toolbox/yopp_sitemip
export PYTHONPATH=$PYTHONPATH:$YDIR
export pid=$$
mkdir $HOME/scratch/yopp.$pid
cd $HOME/scratch/yopp.$pid
ln -s $YDIR/gpfs .
cp -p $YDIR/*.py .
cp -p $YDIR/*.csv .

#Antarctic SOP1:
start=20181116
end=20181208
#end=20190215

tag=$start

export YOPP_base=$HOME/clim_data/yopp

#set -xe
set -x
while [ $tag -le $end ]
do
  #######
  # do the extraction to .nc:

  for cyc in 18
  do
    export YOPP_archive_dir=$YOPP_base/$cyc
    if [ ! -d $YOPP_archive_dir ] ; then
      mkdir $YOPP_archive_dir
    fi

    if [ ! -f $YOPP_archive_dir/ncep_gfs_sflux.$tag$cyc.tgz ] ; then
      time python3 $YDIR/sflux_toyopp.py $cyc $tag
      tar czf ncep_gfs_sflux.$tag$cyc.tgz *.nc
      mv *.nc ncep_gfs_sflux.$tag$cyc.tgz $YOPP_archive_dir
    fi

    if [ ! -f $YOPP_archive_dir/ncep_gfs_pgrb.$tag$cyc.tgz ] ; then
      time python3 $YDIR/pgrb2_toyopp.py $cyc $tag
      tar czf ncep_gfs_pgrb.$tag$cyc.tgz *.nc
      mv *.nc ncep_gfs_pgrb.$tag$cyc.tgz $YOPP_archive_dir
    fi

    if [ ! -f $YOPP_archive_dir/ncep_gfs_pgrb_surf.$tag$cyc.tgz ] ; then
      time python3 $YDIR/pgrb2_surface.py $cyc $tag
      tar czf ncep_gfs_pgrb_surf.$tag$cyc.tgz *.nc
      mv *.nc ncep_gfs_pgrb_surf.$tag$cyc.tgz $YOPP_archive_dir
    fi

    # push the patches to PSL, ECMWF -- interactive only
    #./to_yopp $tag$cyc
      
  done

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
