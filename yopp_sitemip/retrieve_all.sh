#GFS archives:
tag=20210726
d=/NCEPPROD/hpssprod/runhistory/rh2021/202107/$tag
cyc=00

name_base=com_gfs_prod_gfs
for fn in gfs_flux.tar gfs_nca.tar gfs_ncb.tar gfs_pgrb2.tar gfs_pgrb2b.tar 
do
  #htar -tvf ${d}/${name_base}.${tag}_${cyc}.$fn > ${fn}.list
  htar -xvf ${d}/${name_base}.${tag}_${cyc}.$fn > ${fn}.list
done
