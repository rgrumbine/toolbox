#!/bin/sh

set -x
module load HPSS/5.0.2.5

end=20210701
tag=`date +"%Y%m%d"`
#tag=20210529

base=`pwd`
j=0
#Up to 07/##/2018
#pathbase=com_gens_prod_gefs
#Afterwards, up to 2020/02/25
#pathbase=gpfs_hps_nco_ops_com_naefs_prod_gefs
#After 2020/02/25
pathbase=com_naefs_prod_gefs

# 75 is ~2 Tb for .5 GEFS
while [ $j -lt 75 -a \( $tag -ge $end \) ]
#for tag in 20170910 20171012 20171013 20171027 20171108 20171109 20171110 20180119 20180612 20180613   
do
  yy=`echo $tag | cut -c1-4`
  mo=`echo $tag | cut -c5-6`
  dd=`echo $tag | cut -c7-8`
  for hh in 00 
  do

    if [ ! -d gefs.${tag}/${hh} -a \( ! -f winds.${tag}.tar \) ] ; then
      hsi get /NCEPPROD/2year/hpssprod/runhistory/rh${yy}/${yy}${mo}/${yy}${mo}${dd}/${pathbase}.${tag}_${hh}.pgrb2ap5_bc.tar

      if [ -f ${pathbase}.${tag}_${hh}.pgrb2ap5_bc.tar ] ; then
        mkdir -p gefs.${tag}/${hh}
        cd gefs.${tag}/${hh}
        tar xf ${base}/${pathbase}.${tag}_${hh}.pgrb2ap5_bc.tar
        cd $base
        rm ${pathbase}.${tag}_${hh}.pgrb2ap5_bc.tar
      fi
     else
      echo already have $tag
    fi

  done

  j=`expr $j + 1`
  tag=`expr $tag - 1`
  tag=`dtgfix3 $tag`
done
