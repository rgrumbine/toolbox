#!/bin/sh
#Robert Grumbine
#22 December 2016

set -x

#source ../versions/build.ver

module list > /dev/null 2> /dev/null
if [ $? -ne 0 ] ; then
#On a system without the module software
  if [ `uname` == 'Darwin' ] ; then
    export MMAB_BASE=/Users/rmg3/usrlocal/mmablib/
    export MMAB_VER=v3.5.0
  else
    export MMAB_BASE=/usr1/rmg3
    export MMAB_VER=v3.5.0
  fi
  export VER=$MMAB_VER
  export MMAB_INC=$MMAB_BASE/$VER/include/
  export MMAB_LIB="-L ${MMAB_BASE}/$VER/"
  export MMAB_SRC=${MMAB_BASE}/${VER}/sorc/
  #end building on non-module system
else
#on a system with module software, such as wcoss
#  set +x
  module reset
  module load intel PrgEnv-intel
  module list
  env

  set -x
  export MMAB_BASE=~/rgops/mmablib/${MMAB_VER}
  export MMAB_INC=$MMAB_BASE/include
  export MMAB_SRC=$MMAB_BASE/sorc
  export MMAB_LIBF4=$MMAB_BASE/libombf_4.a

fi
export mmablib_ver=${MMAB_VER}
#if [ ! -d mmablib ] ; then
#	git clone --recursive -b operations https://github.com/rgrumbine/mmablib
#fi
#if [ ! -f mmablib/libombf_4.a ] ; then
#	cd mmablib
#	make
#	cd ..
#fi

#set -xe
set -x

module list
make
