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

cd /ncrc/home1/Robert.Grumbine
#list off files to put:
cd scratch
for f in expt1.tar
do
  hsi put $f : ${hpss_dir}/${f}
done
