#!/bin/sh

module load prod_envir

set -x
tag=${tag:-`date +"%Y%m%d"`}

cd  /lfs/h1/ops/dev/dcom
cd $tag
cd seaice/smos-smap
cp -p *.nc $HOME/noscrub/thickness/


