#include "ncepgrids.h"
#include "netcdf.h"

/* Handle errors by printing an error message and exiting with a
 *  * non-zero status. */
#define ERRCODE 2
#define ERR(e) {printf("Error: %s\n", nc_strerror(e)); exit(ERRCODE);}
#define ERR2(e,v) {printf("Error: %s on variable %s\n", nc_strerror(e), v); exit(ERRCODE);}

void range(float &x, float &y);
void range(float &x, float &y) {
  //debug: printf("range %f %f  %f\n",x,y,x-y);
  if (y-x > 180.) {
    //debug: printf("gt %f %f\n",x,y);
    x += 360.;
    //debug: printf("gt %f %f\n",x,y);
  }
  if (y-x < -180) {
    //debug: printf("lt %f %f\n",x,y);
    y += 360.;
    //debug: printf("lt %f %f\n",x,y);
  }
  return;
}



void enter(grid2<float> &param, float *x) ;
void enter(grid2<float> &param, float *x) {
  ijpt loc;
  for (loc.j = 0; loc.j < param.ypoints(); loc.j++) {
  for (loc.i = 0; loc.i < param.xpoints(); loc.i++) {
    if (x[loc.i+ param.xpoints()*loc.j] > 1e20) x[loc.i+ param.xpoints()*loc.j] = 0;
    param[loc] = (float) x[loc.i+ param.xpoints()*loc.j];
  }
  }
  #ifdef DEBUG
  printf("stats: %f %f %f %f\n",param.gridmax(), param.gridmin(), param.average(), param.rms() );
  fflush(stdout);
  #endif

  return;
}

int main(int argc, char *argv[]) {
  osisaf_north<float> nh, lat, lon;
  //osisaf_south<float> sh, lat, lon;
  global_12th<float> out;
  ijpt loc;

  // Read in netcdf information from osisaf
  float *x;
  int ncid, varid;
  int retval;
  x = (float*) malloc(sizeof(float)*lon.xpoints()*lon.ypoints());

  retval = nc_open(argv[1], NC_NOWRITE, &ncid);
  if (retval != 0) ERR(retval);
// Get vars:
  retval = nc_inq_varid(ncid, "lat", &varid);
  if (retval != 0) ERR2(retval, "lat");
  retval = nc_get_var_float(ncid, varid, x);
  if (retval != 0) ERR2(retval, "lat");fflush(stdout);
  enter(lat, x);

  retval = nc_inq_varid(ncid, "lon", &varid);
  if (retval != 0) ERR2(retval, "lon");
  retval = nc_get_var_float(ncid, varid, x);
  if (retval != 0) ERR2(retval, "lon");fflush(stdout);
  enter(lon, x);

  retval = nc_inq_varid(ncid, "ice_conc", &varid);
  if (retval != 0) ERR2(retval, "ice_conc");
  retval = nc_get_var_float(ncid, varid, x);
  if (retval != 0) ERR2(retval, "ice_conc");fflush(stdout);
  //enter(sh, x);
  enter(nh, x);

  nc_close(ncid);

  printf("%f %f\n",lon.gridmax(), lon.gridmin() );
  printf("%f %f\n",lat.gridmax(), lat.gridmin() );
  //printf("%f %f\n",sh.gridmax(), sh.gridmin() );
  printf("%f %f\n",nh.gridmax(), nh.gridmin() );

  float eps = 5.e-1;
  latpt llx, lly;

  for (loc.j = 0; loc.j < nh.ypoints(); loc.j++ ) {
  for (loc.i = 0; loc.i < nh.xpoints(); loc.i++ ) {
    llx = nh.locate(loc);
    llx.lon = -llx.lon;
    if (llx.lon >   180.) {llx.lon -= 360.;}
    if (llx.lon <= -180. && llx.lon != -999.) {llx.lon += 360.;}
    lly.lat = lat[loc];
    lly.lon = lon[loc];
    range(llx.lon, lly.lon);
    if ( fabs(lly.lat-llx.lat) > eps || fabs(lly.lon-llx.lon) > eps) {
      printf("%d %d %f %f %f  %f %f %f\n",loc.i, loc.j, llx.lat, lly.lat, lly.lat-llx.lat, llx.lon, lly.lon, lly.lon-llx.lon);
    }
  }
  }
  //return 0;

  float landval = -999.;
  float nonval  = -999.;
  palette<unsigned char> gg(19, 65);
  printf("lat %f %f\n",lat.gridmax(), lat.gridmin() );
  //out.fromall(lat, landval, nonval);
  printf("lon %f %f\n",lon.gridmax(), lon.gridmin() );
  out.fromall(lon, landval, nonval);
  printf("out %f %f\n",out.gridmax(landval), out.gridmin() );

  fijpt floc;
  ijpt ijx, ijy;

  for (loc.j = 0; loc.j < lat.ypoints() ; loc.j++) {
  for (loc.i = 0; loc.i < lat.xpoints() ; loc.i++) {
     llx  = lat.locate(loc);
     floc = out.locate(llx);
     ijy.i = (int) (floc.i+0.5);
     ijy.j = (int) (floc.j+0.5);
     if (out[ijy] != landval) {
       //if (fabs(out[ijy] - lat[loc]) > eps) {
       if (fabs(out[ijy] - lon[loc]) > eps) {
         //printf("delta %d %d  %f %f  %f\n",loc.i, loc.j, out[ijy], lat[loc], out[ijy]-lat[loc]);
         printf("delta %d %d  %f %f  %f\n",loc.i, loc.j, out[ijy], lon[loc], out[ijy]-lon[loc]);
       }
     }
  }
  }

  return 0;
}
