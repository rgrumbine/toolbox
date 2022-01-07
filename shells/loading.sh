#source /lustre/f2/pdata/esrl/gsd/contrib/lua-5.1.4.9/init/init_lmod.sh

sacctmgr list associations user=$USER -p
#sacctmgr list qos

source /lustre/f2/pdata/esrl/gsd/contrib/lua-5.1.4.9/init/init_lmod.sh
module purge
module load intel
module load PrgEnv-intel
module load hsi
module list
