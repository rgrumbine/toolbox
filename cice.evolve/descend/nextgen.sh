#!/bin/sh

export old=gen4
export next=gen5

# link parents points to directory with all the previous parameter sets
if [ -d parents ] ; then
  rm parents
fi
ln -s $old parents

# make a directory to save + point to for next gen
if [ ! -d $next ] ; then
  mkdir $next
fi

# parm.gen2 is the full parameter set
# fatal is the collection of fatal mutations
# final argument is the list of parent numbers from the old generation
python3 descend.py parm.gen1 fatal ${next}in

# Copy files to the running directories
export OPT=$HOME/rgdev/CICE/configuration/scripts/options

if [ $OPT != "" ] ; then
  rm $OPT/set_nml.evo?*
  rm $OPT/../tests/exptlist.ts

  cp -p set_nml.evo* $OPT
  cp -p exptlist.ts $OPT/../tests
else
  echo must export OPT, pointing to the configuration/scripts/options directory
fi

# Move control files to a generation directory
mv set_nml.evo* exptlist.ts ${next}
