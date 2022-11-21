
#Indices to naming list
short    = int(0)
standard = int(1)
yopp     = int(2)

grib_to_netcdf = {
# "grib_short_name" : ["standard_name", "netcdf_long_name"],
# 2d vars (sflux output from GFS)

# 3d vars (pgrb2 and pgrb2b output from GFS)
#grib short name : ["" , ""]
"gh" : ["zg",  "Geopotential height", "geopotential_height"], 
"t"  : ["ta",  "Temperature", "air_temperature"],
"u"  : ["ua",  "Eastward wind component", "eastward_wind"], 
"v"  : ["va",  "Northward wind component", "northward_wind"], 
"w"  : ["wap", "Vertical large-scale wind in pressure coordinates","lagrangian_tendency_of_air_pressure"], 
"r"  : ["hur", "Relative humidity", "relative_humidity"] 
}
#usage:
#list[short, standard name, ncname] = grib_to_netcdf["grib_short_name"]

print(grib_to_netcdf["w"])
print(grib_to_netcdf["w"][short])
print(grib_to_netcdf["w"][standard])
print(grib_to_netcdf["w"][yopp])
