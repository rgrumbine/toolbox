#!/bin/sh

tag=20100101
while [ $tag -le 20220801 ]
do
	if [ -d $tag ] ; then
		mv $tag sice.$tag
	fi
	tag=`expr $tag + 1`
	tag=`dtgfix3 $tag`
done
