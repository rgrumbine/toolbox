#!/bin/sh -l
#SBATCH -J test1
#SBATCH --account=nggps_emc
#SBATCH --clusters=es
#SBATCH --partition=rdtn
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=50
#SBATCH -e alpha.err
#SBATCH -o alpha.out

source /lustre/f2/pdata/esrl/gsd/contrib/lua-5.1.4.9/init/init_lmod.sh
module load hsi
module list

hpss_dir=/NCEPDEV/emc-marine/5year/Robert.Grumbine/
hsi "ls -l $hpss_dir"
cd ~/rgdev
hsi "get ${hpss_dir}/CICE_data.tar"

ls -l
