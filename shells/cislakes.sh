#!/bin/sh

cd ~/noscrub/lakes
wget ftp://ice-glaces.ec.gc.ca/*.txt
chmod a-w *lakeice.txt

#echo mget '*.txt' > l
#echo quit >> l
#cat l | ftp ice-glaces.ec.gc.ca 2>> lakes.err >> lakes.out
#rm l
#ftp://ice-glaces.ec.gc.ca/
#user: primary
#password: statistics
#files -- DDMMYYYY_lakeice.txt 
