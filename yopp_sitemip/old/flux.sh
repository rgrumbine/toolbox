#!/bin/bash 
# #!/bin/bash --login
#SBATCH --ntasks=1 -p service 
#SBATCH -A fv3-cpu
#SBATCH -q batch 
#SBATCH -o slurm-get-%j.out
#SBATCH -J oct1_mosaic
#SBATCH -e oct1_mosaic
#SBATCH -o oct1_mosaic
#SBATCH -t 7:55:00
#  #SBATCH -N 1

#SBATCH --mail-type FAIL
#SBATCH --mail-user USER@system

module list
#-------------------------- Reference -------------------------------
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

#Mosaic:
start=20191001
#end=20201012
end=20191001

tag=$start

set -x
for cyc in 00
do
  while [ $tag -le $end ]
  do
    #GFS archives:
    yy=`echo $tag | cut -c1-4`
    yrmo=`echo $tag | cut -c1-6`
  
    d=/NCEPPROD/hpssprod/runhistory/rh${yy}/${yrmo}/$tag
    if [ $tag -lt 20191001 ] ; then
      out=gpfs/hps/nco/ops/com/gfs/prod/gfs.$tag
    else
      out=gpfs/dell1/nco/ops/com/gfs/prod/gfs.$tag
    fi
    #out=... for newer times
  
    if [ ! -d $out ] ; then
      if [ $tag -ge 20191001 ] ; then

        #current: 20210726 name_base=com_gfs_prod_gfs
        # 20191001:
        # sflux -- hourly to 120, 3 hrly to 384
        # pgrb2 -- 3 hourly to 384 

        name_base=gpfs_dell1_nco_ops_com_gfs_prod_gfs
        echo zzz name_base = $name_base
        echo zzz tag = $tag zzz

        for fn in gfs_flux.tar 
        do
          htar -xf ${d}/${name_base}.${tag}_${cyc}.$fn
          hsi get ${d}/${name_base}.${tag}_${cyc}.$fn
        done
  
      elif [ $tag -lt 20191001 ] ; then
        name_base=gpfs_hps_nco_ops_com_gfs_prod_gfs
        for fn in sfluxgrb.tar pgrb2_0p25.tar 
        do
          #current: 20210726 htar -xvf ${d}/${name_base}.${tag}_${cyc}.$fn > ${fn}.list
          #echo htar -xvf ${d}/${name_base}.${tag}_${cyc}.$fn 
    
          #old: 20180201
          htar -xvf ${d}/${name_base}.${tag}${cyc}.$fn 
        done
        mv gfs.t${cyc}z.pgrb* $out
      fi
    fi

    tag=`expr $tag + 1`
    tag=`$HOME/bin/dtgfix3 $tag`
  done
done
