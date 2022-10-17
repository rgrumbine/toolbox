#!/bin/sh

#General retrieval of data sets for the day, in approximate order of increasing size
# Robert Grumbine 26 September 2022

time ./cislakes.sh #-- kb/wk
time ./nic_edge.sh #-- kb/day

#iabp
time ./iabp_dcomdev #-- 500 Mb/day
time ./iabp.wget    #-- can be up to a few Gb, but updates only monthly

time ./osisaf      # --  76 Mb/day
time ./get_cafs.sh # -- 500 Mb/day
time ./nsidc       # updates only about quarterly

#submit jobs that reference hpss to q so that data transfer nodes+queues can be used
qsub ./reget.2yr.sh # -- 2Gb/day

qsub ./gefs_get.sh   #  ./gefs_thin.sh, ./gefs_clean.sh -- 1 Gb/day
time   ./gefs_thin.sh   # this winds up cleaning yesterday and before, 
                        # since the queue won't respond instantly

#sice
#ims

#While large volumes, these are disk to disk copy from com to my space
time ./rtofs_cice_copy.sh # -- 27 Gb/day
time ./giops.sh           # -- 28 Gb/day 
#viirs -- 32 Gb/day
-rwxr-xr-x 1 robert.grumbine couple 398 Oct 17 17:57 iabp_dcomdev
-rwxr-xr-x 1 robert.grumbine emc    460 Oct 17 17:51 iabp.wget
