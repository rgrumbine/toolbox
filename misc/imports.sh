#!/bin/sh

#lightweight check that necessary python modules are available

module load intel/2022.1.2
module load python/3.8.6
module load proj/7.1.0
module load geos/3.8.1

python3 imports.py 

