#!/bin/sh -l
#SBATCH -J test1
#SBATCH --account=nggps_emc
#SBATCH --clusters=es
#SBATCH --partition=rdtn
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=150
#SBATCH -e beta.err
#SBATCH -o beta.out

cd ~/rgdev
hpss_dir=/NCEPDEV/emc-marine/5year/Robert.Grumbine/

source /lustre/f2/pdata/esrl/gsd/contrib/lua-5.1.4.9/init/init_lmod.sh
module load hsi
module list

hsi "ls -l $hpss_dir"
for f in nsidc.nc.tar
do
  hsi get ${hpss_dir}/${f}
done

ls -l
