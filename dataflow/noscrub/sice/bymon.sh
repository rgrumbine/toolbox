#!/bin/sh

yy=2023
for mm in 04 05
do
    tar cf ../sice.${yy}${mm}.tar sice.${yy}${mm}??
done
