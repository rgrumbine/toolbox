#!/bin/sh
#
source ~/rgdev/toolbox/amsr2.filter/nest

#tag=20240101
#while [ $tag -le 20240303 ]
for tag in 20240303 
#for tag in 20220313 20220129 20220312 20220122 20220101 20221010 20220102 20220127 20220125 20231010 20230301 20231002 20231021 20230323 20230901 20231028 20230529 20231026 20231108 20240208 20240207 20240209 20240103 20240218 20240206 20240102 20240111 20240131 20240217 20220130 20230321 20240106 20240219 20240118 20240223 20240221 20240220 20240119
do
  yy=`echo $tag | cut -c1-4`
  d=`echo $tag | cut -c5-8`

  if [ -d ../$yy/$d ] ; then
    if [ ! -f newfilt/f10out.$tag ] ; then
      ln -sf ../$yy/$d/f11 .
      ln -sf ../$yy/$d/f00 .
      ln -sf ../$yy/$d/f01 .
      ln -sf ../$yy/$d/f10 .
      
      time python3 apply.py $tag 
      mv f??out.$tag newfilt
    fi

  fi

done


