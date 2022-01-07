#!/bin/sh

#approximately 4 min run time if not much to update
cd ~/noscrub/


base=ftp://sidads.colorado.edu/pub/DATASETS/
for dname in nsidc0001_polar_stereo_tbs nsidc0051_gsfc_nasateam_seaice 
do
  wget -q --mirror ${base}/$dname
done

exit

# Added images directories give addl 70 Gb to this: NOAA/G02135 

# All files > 18 years old as of 1 May 2014:
nsidc0007_smmr_radiance_seaice_v01 
# 2 yrs
nsidc0009_esmr_seaice
nsidc_0077_esmr_tbs
nsidc0077_esmr_tbs 
#
ftp://sidads.colorado.edu/DATASETS/NOAA/G02135/
