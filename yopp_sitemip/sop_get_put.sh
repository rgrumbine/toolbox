#!/bin/sh

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

#Arctic SOP1:
start=20180201
#end=20180331
end=20180201

tag=$start
. python_load

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
    for cyc in 00 
    do

      #current: 20210726 name_base=com_gfs_prod_gfs
      #for fn in gfs_flux.tar gfs_pgrb2.tar gfs_pgrb2b.tar 

      name_base=gpfs_hps_nco_ops_com_gfs_prod_gfs
      for fn in sfluxgrb.tar pgrb2_0p25.tar 
      do
        #current: 20210726 htar -xvf ${d}/${name_base}.${tag}_${cyc}.$fn > ${fn}.list
        #echo htar -xvf ${d}/${name_base}.${tag}_${cyc}.$fn 
  
        #old: 20180201
        htar -xvf ${d}/${name_base}.${tag}${cyc}.$fn 
      done
      mv gfs.t${cyc}z.pgrb* $out
    done
  fi

  #######
  # do the extraction to .nc:
  #   python3 sflux_toyopp.py $cyc $tag
  #   python3 pgrb2_toyopp.py $cyc $tag
  #   tar czf ncep_gfs.$tag.tgz *.nc
  #   rm *.nc
  # push the patches to PSL, ECMWF
  #   to_yopp
  #######
  # remove the huge gfs files
  #######

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
#which python3

