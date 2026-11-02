#!/bin/sh
##ursa
#SBATCH -J climo
#SBATCH -e climo.err
#SBATCH -o climo.out
#SBATCH -t 7:55:00
#SBATCH -q batch
#SBATCH -A marine-cpu
#SBATCH -N 1
#SBATCH --mem=8g

# Robert Grumbine
# 30 October 2026

source $HOME/rg/env3.13/bin/activate

cd /home/Robert.Grumbine/rgdev/toolbox/epoch/

for parm in PRMSL_meansealevel \
    PWAT_entireatmosphere_consideredasasinglelayer_ \
    TMP_surface ICETK_surface LANDFRC_surface TMP_2maboveground SPFH_2maboveground \
    UGRD_10maboveground VGRD_10maboveground SHTFL_surface LHTFL_surface \
    USWRF_surface LAND_surface ICEC_surface FDNSSTMP_surface
#for parm in PRMSL_meansealevel 
do
  trim=`echo $parm | cut -f1 -d_`
  echo $trim
  if [ ! -f  epoch2007_${trim}.nc ] ; then
    time python3 climo_trend.py $parm
    mv epoch2007.nc epoch2007_${trim}.nc
  fi
done

for parm in HGT_1mb HGT_10mb HGT_200mb HGT_500mb HGT_700mb HGT_850mb 
do
  if [ ! -f  epoch2007_${parm}.nc ] ; then
    time python3 climo_trend.py $parm
    mv epoch2007.nc epoch2007_${parm}.nc
  fi
done
