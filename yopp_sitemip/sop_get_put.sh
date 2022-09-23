#!/bin/sh

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
  #for cyc in 00 06 12 18
  for cyc in 00 
  do

    #current: 20210726 name_base=com_gfs_prod_gfs
    #for fn in gfs_flux.tar gfs_pgrb2.tar gfs_pgrb2b.tar 

    name_base=gpfs_hps_nco_ops_com_gfs_prod_gfs
    for fn in sfluxgrb.tar pgrb2_0p25.tar 
    do
      #current: 20210726 htar -xvf ${d}/${name_base}.${tag}_${cyc}.$fn > ${fn}.list

      htar -xvf ${d}/${name_base}.${tag}${cyc}.$fn > ${fn}.list
      #echo htar -xvf ${d}/${name_base}.${tag}_${cyc}.$fn 
    done

    #######
    # do the extraction to .nc
    # python3 leveltype.py $cyc $tag
    #######
    # remove the huge gfs files
    # push the patches to PSL, ECMWF
    #######

  done

  tag=`expr $tag + 1`
  tag=`$HOME/bin/dtgfix3 $tag`
done
which python3
