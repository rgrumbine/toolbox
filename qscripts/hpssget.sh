#!/bin/sh -l
#SBATCH -J test1
#SBATCH --account=nggps_emc
#SBATCH --clusters=es
#SBATCH --partition=rdtn
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=150
#SBATCH -e alpha.err
#SBATCH -o alpha.out

#cd ~/rgdev
hpss_dir=/NCEPDEV/emc-marine/5year/Robert.Grumbine/

source /lustre/f2/pdata/esrl/gsd/contrib/lua-5.1.4.9/init/init_lmod.sh
module load hsi
module list

hsi "ls -l $hpss_dir"
#list off files to get:
#for f in nsidc.tb.tar osisaf/osisaf.2005t2009.tar ice5min.tar
for f in nsidc.cdrv4.tar
do
  hsi get ${hpss_dir}/${f}
done
