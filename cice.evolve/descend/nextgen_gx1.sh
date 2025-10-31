#!/bin/sh

export next=gengx1_5

# link parents points to directory with all the previous parameter sets
if [ -d parents ] ; then
  rm parents
fi

# make a directory to save + point to for next gen
if [ ! -d $next ] ; then
  mkdir $next
fi

# parm.gen2 is the full parameter set
# fatal is the collection of fatal mutations
# final argument is the list of parent numbers from the old generations
python3 descend_gx1.py parm.gen2 fatal ${next}in

# Copy files to the running directories
export OPT=$HOME/rgdev/CICE/configuration/scripts/options

if [ $OPT != "" ] ; then
  rm $OPT/set_nml.evo?*
  rm $OPT/../tests/exptlist1.ts

  cp -p set_nml.evo* $OPT
  cp -p exptlist1.ts $OPT/../tests
else
  echo must export OPT, pointing to the configuration/scripts/options directory
fi

# Move control files to a generation directory
mv set_nml.evo* exptlist1.ts ${next}
