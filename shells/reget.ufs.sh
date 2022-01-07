#!/bin/sh

if [ $# -ne 1 ] ; then
  echo need exactly 1 argument -- directory name to check in to
  exit 1
fi
export DNAME=$1

git clone https://github.com/ufs-community/ufs-weather-model.git $DNAME
cd $DNAME
#git checkout ufs-v1.1.0
#git checkout ufs-v2.0.0
git checkout develop
git submodule update --init --recursive

cd tests
./rt.sh -e


