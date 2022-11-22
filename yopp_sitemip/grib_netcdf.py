#usage:
# "grib_short_name" : ["VariableName", "standard_name", "netcdf_long_name"],
#list[short, standard name, ncname] = grib_to_netcdf["grib_short_name"]

#Indices to naming list
short    = int(0)
standard = int(1)
yopp     = int(2)

# Begin dictionary -----------------------------------------------------------------
grib_to_netcdf = {
#Both sflux and pgrb2:
"u"  : ["ua",  "Eastward wind component", "eastward_wind"], 
"v"  : ["va",  "Northward wind component", "northward_wind"], 
"gh" : ["zg",  "Geopotential height", "geopotential_height"], 

# 2d vars (sflux output from GFS)
"10u"   : [ "uas",  "Near-surface (10m) eastward wind", "eastward_wind" ],
"10v"   : [ "vas",  "Near-surface (10m) northward wind", "northward_wind" ],
"2t"    : [ "tas",  "Near-surface (2m) air temperature", "air_temperature" ],
"al"    : [ "albs",  "Surface albedo", "surface_albedo" ],
"ci"    : [ "siconc",  "Sea-ice concentration (area fraction)", "sea_ice_area_fraction" ],
"dlwrf" : [ "rlds",  "Downward surface long-wave radiation", "surface_downwelling_longwave_flux_in_air" ],
"dswrf" : [ "rsds",  "Downward short-wave radiation at the surface", "surface_downwelling_shortwave_flux_in_air" ],
"gflux" : [ "hfds",  "Ground heat flux", "downward_heat_flux_at_ground_level_in_soil" ],
"hpbl"  : [ "zmla",  "Height of atmospheric boundary layer", "atmosphere_boundary_layer_thickness" ],
"icetk" : [ "sithick",  "Sea-ice thickness", "sea_ice_thickness" ],
"lhtfl" : [ "hfls_bulk",  "Surface turbulent latent heat flux (bulk method)", "surface_upward_latent_heat_flux" ],
"prate" : [ "pr",  "Total precipitation of water in all phases per unit area", "precipitation_flux" ],
"q"     : [ "huss",  "Near-surface (2m) specific humidity", "specific_humidity" ],
"sde"   : [ "snd",  "Surface snow thickness", "surface_snow_thickness" ],
"sdwe"  : [ "snw",  "Snow water equivalent", "liquid_water_content_of_surface_snow" ],
"sp"    : [ "ps",  "Surface pressure", "surface_air_pressure" ],
"tcc"   : [ "clt",  "Total cloud cover", "cloud_area_fraction" ],
"uflx"  : [ "uw",  "Eastward turbulent momentum flux", "downward_eastward_momentum_flux_in_air" ],
"vflx"  : [ "vw",  "Northward turbulent momentum flux", "downward_northward_momentum_flux_in_air" ],
"uswrf" : [ "rsut",  "Top-of-atmosphere outgoing short-wave radiation", "toa_outgoing_shortwave_flux" ],
"uswrf" : [ "rsus",  "Upward surface short-wave radiation", "surface_upwelling_shortwave_flux_in_air" ],
"ulwrf" : [ "rlut",  "Top-of-atmosphere outgoing long wave radiation", "toa_outgoing_longwave_flux" ],
"ulwrf" : [ "rlus",  "Upward surface long-wave radiation", "surface_upwelling_longwave_flux_in_air" ],
#"sr" : (does EMC distinguish between the two?) 
##grib2_name : [ z0h ,  "Surface roughness for heat", "surface_roughness_length_for_heat_in_air" ],
##grib2_name : [ z0m ,  "Surface roughness for momentum", "surface_roughness_length_for_momentum_in_air" ],

# 3d vars (pgrb2 and pgrb2b output from GFS)
"t"  : ["ta",  "Temperature", "air_temperature"],
"w"  : ["wap", "Vertical large-scale wind in pressure coordinates","lagrangian_tendency_of_air_pressure"], 
"r"  : ["hur", "Relative humidity", "relative_humidity"] 
}

# End dictionary -----------------------------------------------------------------


# list of grib2 short names in sflux, but not HK (42) ------------------------------
nothk = [
"acond",
"cduvb",
"cnwat",
"cpofp",
"cprat",
"csdlf",
"csdsf",
"csulf",
"csusf",
"cwork",
"duvb",
"evbs",
"evcw",
"fldcp",
"fricv",
"lsm",
"nbdsf",
"nddsf",
"orog",
"pevpr",
"pwat",
"qmax",
"qmin",
"sbsno",
"shtfl",
"sltyp",
"snowc",
"soill",
"soilw",
"ssrun",
"ssw",
"st",
"SUNSD",
"tmax",
"tmin",
"trans",
"u-gwd",
"vbdsf",
"vddsf",
"veg",
"vgtyp",
"watr",
"wilt"
]

#--------------------------------------------------------------
# Demonstration code
#print(grib_to_netcdf["w"][short])
#print(grib_to_netcdf["w"][standard])
#print(grib_to_netcdf["w"][yopp])
#
#print(grib_to_netcdf["10u"])
#
#print("trans" in nothk)
#print("w" in nothk)

