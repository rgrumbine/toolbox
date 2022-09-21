#!/bin/sh

if [ $# -ne 1 ] ; then
  echo need one and only one argument -- start date of the forecast
  exit 1
fi
base=$1

for mem in 01 02 03 04
do
  tag=$base
  d=0
  rm -f *anl*.tar
  while [ $d -le 183 ]
  do
    d=`expr $d + 1`
    tag=`expr $tag + 1` 
    tag=`dtgfix3 $tag`

    rm -f ocnf${tag}06.* flxf${tag}06.*
    rm -f ocnf${tag}12.* flxf${tag}12.*
    rm -f ocnf${tag}18.* flxf${tag}18.*

    wgrib2 ocnf${tag}00.${mem}.${base}00.grb2 | grep ICE | wgrib2 -i ocnf${tag}00.${mem}.${base}00.grb2 -grib ocnf.ice.${tag}00.$mem.${base}00
    wgrib2 flxf${tag}00.${mem}.${base}00.grb2 | grep ICE | wgrib2 -i flxf${tag}00.${mem}.${base}00.grb2 -grib flxf.ice.${tag}00.$mem.${base}00

  done
done
find . -size 0 -exec rm {} \;
