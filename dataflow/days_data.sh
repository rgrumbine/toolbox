#!/bin/bash

#General retrieval of data sets for the day, in approximate order of increasing size
# Robert Grumbine 26 September 2022
#

cd $HOME/rgdev/toolbox/dataflow
if [ $? -ne 0 ] ; then
	echo could not cd to dataflow directory
	exit 1
fi
#env > env.initial

time ./cislakes.sh #-- kb/wk
time ./nic_edge.sh #-- kb/day

#iabp
time ./iabp_dcomdev #-- 500 Mb/day
time ./iabp.wget    #-- can be up to a few Gb, but updates only monthly

time ./osisaf      # --  76 Mb/day
time ./ims.wget    # -- 0.5 Mb/day, but may get several months at a time
time ./nsidc       # updates only about quarterly

time ./get_cafs.sh # -- 500 Mb/day

#submit jobs that reference hpss to q so that data transfer nodes+queues can be used
echo zzz set up modules
source /usr/share/lmod/lmod/init/bash
module list
echo zzz preceding was list of modules from days_data.sh

/opt/pbs/bin/qsub ./reget.2yr.sh # -- 2Gb/day, ssmi-s, amsr2

/opt/pbs/bin/qsub ./gefs_get.sh   #  ./gefs_thin.sh, ./gefs_clean.sh -- 1 Gb/day
time   ./gefs_thin.sh   # this winds up cleaning yesterday and before, 
                        # since the queue won't respond instantly

/opt/pbs/bin/qsub sice.reget.sh   # 5-10 Gb/day, opnl sea ice analysis

#While large volumes, these are disk to disk copy from com to my space
/opt/pbs/bin/qsub ./rtofs_cice_copy.sh # -- 27 Gb/day
time ./giops.sh           # -- 28 Gb/day 
#viirs -- 32 Gb/day

#env > env.final
