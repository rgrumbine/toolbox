#!/bin/bash --login
#SBATCH -J trans_weather
#SBATCH -e trans_weather.err
#SBATCH -o trans_weather.out
#SBATCH -t 7:55:00
#  #SBATCH -t 0:29:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#  #SBATCH -A fv3-cpu
#SBATCH -N 1
#SBATCH --mail-type FAIL
#SBATCH --mail-user USER@system

module list
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

cd $HOME/rgdev/toolbox/yopp_sitemip

#Arctic SOP1:
start=20180201
end=20180331
#end=20180215

tag=$start

#set -xe
set -x
while [ $tag -le $end ]
do
  #GFS archives:
  yy=`echo $tag | cut -c1-4`
  yrmo=`echo $tag | cut -c1-6`

  d=/NCEPPROD/hpssprod/runhistory/rh${yy}/${yrmo}/$tag
  out=gpfs/hps/nco/ops/com/gfs/prod/gfs.$tag
  #out=... for newer times

  if [ ! -d $out ] ; then
    #for cyc in 00 06 12 18
    for cyc in 12 
    do

      #current: 20210726 name_base=com_gfs_prod_gfs
      #for fn in gfs_flux.tar gfs_pgrb2.tar gfs_pgrb2b.tar 

      name_base=gpfs_hps_nco_ops_com_gfs_prod_gfs
      for fn in sfluxgrb.tar pgrb2_0p25.tar 
      do
        #current: 20210726 htar -xvf ${d}/${name_base}.${tag}_${cyc}.$fn > ${fn}.list
        #echo htar -xvf ${d}/${name_base}.${tag}_${cyc}.$fn 
  
        #old: 20180201
        #htar -tvf ${d}/${name_base}.${tag}${cyc}.$fn 
        htar -xvf ${d}/${name_base}.${tag}${cyc}.$fn 
      done
      mv gfs.t${cyc}z.pgrb* $out
    done
  fi

  #######
  # remove the huge gfs files
  #######

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
