import os
import sys

import numpy
import netCDF4 

def enthalpy_snow(Tsfcn, vsnon):
  enthalpy = Tsfcn
  rho_snow = 330.0
  cp = 2160.0
  L = 3.34e5
  enthalpy = -rho_snow*(cp*Tsfcn + L)*vsnon

stresses = ["uvel", "vvel", "strocnxT", "strocnyT", "stressp_1", "stressp_2", "stressp_3", "stressp_4", "stressm_1", "stressm_2", "stressm_3", "stressm_4", "stress12_1", "stress12_2", "stress12_3", "stress12_4"]

# For reading: -------------------------------------------
model_in  = netCDF4.Dataset(sys.argv[1], 'r')
model_out = netCDF4.Dataset(sys.argv[2], "w", format="NETCDF4")

#After https://stackoverflow.com/questions/13936563/copy-netcdf-file-using-python
# Create the dimensions of the file
for name, dim in model_in.dimensions.items():
    model_out.createDimension(name, len(dim) if not dim.isunlimited() else None)

# Copy the global attributes
model_out.setncatts({a:model_in.getncattr(a) for a in model_in.ncattrs()})

# Create the variables in the file
for name, var in model_in.variables.items():
    model_out.createVariable(name, var.dtype, var.dimensions)

    # Copy the variable attributes
    model_out.variables[name].setncatts({a:var.getncattr(a) for a in var.ncattrs()})

    # Copy the variables values (as 'f4' eventually)
    model_out.variables[name][:] = model_in.variables[name][:]

    #name = aicen, vicen, vvel, uvel, ...
    print(name, var.dimensions, flush=True)
    
    #if (name == "aicen"):
    #  print(name, model_out.variables[name][:].max(), model_out.variables[name][:].min() )
    # Step with some editing. Stresses are actually unused (confirmed by expt)
    if name in stresses:
      model_out.variables[name][:] = 0.0 
    if (name == "qsno001"):
        v = model_in.variables["vsnon"][:]
        t = model_in.variables["Tsfcn"][:]
        x = enthalpy_snow(t, v)
        model_out.variables["qsno001"][:] = x


# Save the file
model_out.close()

#aicen ('ncat', 'nj', 'ni')
#vicen ('ncat', 'nj', 'ni')
#Tsfcn ('ncat', 'nj', 'ni')
#iceumask ('nj', 'ni')
#vsnon ('ncat', 'nj', 'ni')
#qsno001 ('ncat', 'nj', 'ni')
#frz_onset ('nj', 'ni')
#Tin ('nilyr', 'ncat', 'nj', 'ni')
#  Enthalpies:
#qice001 ('ncat', 'nj', 'ni')
#qice002 ('ncat', 'nj', 'ni')
#qice003 ('ncat', 'nj', 'ni')
#qice004 ('ncat', 'nj', 'ni')
#qice005 ('ncat', 'nj', 'ni')
#qice006 ('ncat', 'nj', 'ni')
#qice007 ('ncat', 'nj', 'ni')
#  Salinities:
#sice001 ('ncat', 'nj', 'ni')
#sice002 ('ncat', 'nj', 'ni')
#sice003 ('ncat', 'nj', 'ni')
#sice004 ('ncat', 'nj', 'ni')
#sice005 ('ncat', 'nj', 'ni')
#sice006 ('ncat', 'nj', 'ni')
#sice007 ('ncat', 'nj', 'ni')
#  Radiation:
#scale_factor ('nj', 'ni')
#coszen ('nj', 'ni')
#swvdr ('nj', 'ni')
#swvdf ('nj', 'ni')
#swidr ('nj', 'ni')
#swidf ('nj', 'ni')
