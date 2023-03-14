#PBS -N meval
#PBS -o meval
#PBS -j oe
#PBS -A ICE-DEV
#PBS -q dev
#PBS -l walltime=0:10:00
#PBS -l select=1:ncpus=1

set -x

#------------------------------------------------------------------------
export pid=$$
PTMP=/lfs/h2/emc/wx21rg/eval.$pid
mkdir -p $PTMP
cd $PTMP
if [ $? -ne 0 ] ; then
  echo could not cd to running directory, aborting
  exit 1
fi

. $HOME/rgdev/toolbox/python_load.wcoss2
export PYTHONPATH=$PYTHONPATH:$HOME/rgdev/ice_scoring/gross_checks/shared


today=`date +"%Y%m%d"`

#------------------------------------------------------------------------
#   Ice edge verification
#
. $HOME/rgdev/ice_scoring/NCEP_si_verf/ice_edge/vs_nichr/bootstrap.sh

type=edge

#parse nic edge + update persistence scores
time $HOME/rgdev/ice_scoring/NCEP_si_verf/ice_edge/vs_nichr/runup.sh

#score model(s)
for model in rtofs_cice
do
  time python3 rtofs_cice.py $today
done

#------------------------------------------------------------------------
# Gross check Run time is about 2 minutes per day on rtofs_cice

type=gross

export GDIR=$HOME/rgdev/ice_scoring/gross_checks
cd $GDIR

export modelin=$HOME/noscrub/model_intercompare/rtofs_cice
export MODDEF=$HOME/rgdev/ice_scoring/model_definitions

export modelout=$HOME/noscrub/model_intercompare/rtofs_cice_gross
if [ ! -d $modelout ] ; then
  mkdir -p $modelout
  if [ $? -ne 0 ] ; then
    echo could not make output directory for gross checks
    exit 1
  fi
fi

for model in rtofs_cice
do
  #gross
  for lead in n00 f24 f48 f72 f96 f120 f144 f168 f192
  do
      if [ -f $modelin/rtofs.${tag}/rtofs_glo.t00z.${lead}.cice_inst ] ; then
        time python3 $GDIR/rtofs_cice.py \
          $modelin/rtofs.${tag}/rtofs_glo.t00z.${lead}.cice_inst \
          rtofs_cice/rtofs_cice.extremes fly > $modelout/beta.${today}.${lead}
      fi
  done
  # Make figures
  cat $modelout/beta.${today}.* > a
  time python3 $GDIR/plot_errs.py a
  mv ij_errs.png $modelout/ij_errs.$today.png
  mv ll_errs.png $modelout/ll_errs.$today.png
done

#------------------------------------------------------------------------
#threat scores:
#

#------------------------------------------------------------------------
exit
#------------------------------------------------------------------------
-rw-r--r-- 1 robert.grumbine couple 0 Mar  7 16:35 rtofs_cice_edge
-rw-r--r-- 1 robert.grumbine couple 0 Mar  7 16:35 rtofs_cice_gross
-rw-r--r-- 1 robert.grumbine couple 0 Mar  7 16:35 rtofs_cice_threat
-rw-r--r-- 1 robert.grumbine couple 0 Mar  7 16:36 cafs
-rw-r--r-- 1 robert.grumbine couple 0 Mar  7 16:36 giops
