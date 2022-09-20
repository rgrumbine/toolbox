#!/bin/sh

tag=20100101
while [ $tag -le 20220101 ]
do
	if [ -f gefs.$tag.tar ] ; then
		mv gefs.$tag.tar winds.$tag.tar
	fi
	tag=`expr $tag + 1`
	tag=`dtgfix3 $tag`
done
