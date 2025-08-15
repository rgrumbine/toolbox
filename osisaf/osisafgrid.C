#include "ncepgrids.h"
#include "netcdf.h"

/* Handle errors by printing an error message and exiting with a
 *  * non-zero status. */
#define ERRCODE 2
#define ERR(e) {printf("Error: %s\n", nc_strerror(e)); exit(ERRCODE);}
#define ERR2(e,v) {printf("Error: %s on variable %s\n", nc_strerror(e), v); exit(ERRCODE);}

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


template <class T>
class osisaf_south : public psgrid<T> {
  public:
    osisaf_south(void);
    //osisaf_south(osisaf_south<T> &);
};
template<class T>
osisaf_south<T>::osisaf_south(void) {
  this->nx = 790;
  this->ny = 830;
  this->dx = 10e3;
  this->dy = 10e3;
  this->xorig = -this->dx*(395 + .0);
  this->yorig = -this->dy*(435 - 1.0);
  this->sgn  = -1.0;
  this->slat =  70.0;
  this->slon = -90.0;

// Calculate parameters here for later calculation (recalculate needed when
//   slat != 60.0
  double eccen2 = parameters::eccen2;
  double eccen  = sqrt(eccen2);
  this->sl = this->slat / parameters::degrees_per_radian;
  this->cm = cos(this->sl)/ sqrt(1.0-eccen2*sin(this->sl)*sin(this->sl) );
  this->tnaught  = tan(M_PI_4 - this->sl/2.) /
           pow(  ((1.0 - eccen*sin(this->sl))/(1.0+eccen*sin(this->sl))), eccen/2.);

  ijpt f;
  f.i = 0; f.j = 0;
  this->first_longitude = (this->locate(f)).lon;


  this->grid = new T[this->nx*this->ny] ;
  if (this->grid == (T *) NULL) { cout << "Failed to new in osisaf_south(void)\n";
    cout.flush(); }

  return;
}



template <class T>
class osisaf_north : public psgrid<T> {
  public:
    osisaf_north(void);
    //osisaf_north(osisaf_north<T> &);
};
template<class T>
osisaf_north<T>::osisaf_north(void) {
  this->nx = 760;
  this->ny = 1120;
  this->dx = 10e3;
  this->dy = 10e3;
  //-385, -535, 375, 585
  //this->xorig = this->dx*(-385);
  //this->yorig = this->dy*(-535);
  this->xorig = -this->dx*(375 + .5);
  this->yorig = -this->dy*(585 - .5);
  this->sgn = 1.0;
  this->slat = 70.0;
  this->slon = -225.0;

// Calculate parameters here for later calculation (recalculate needed when
//   slat != 60.0
  double eccen2 = parameters::eccen2;
  double eccen  = sqrt(eccen2);
  this->sl = this->slat / parameters::degrees_per_radian;
  this->cm = cos(this->sl)/ sqrt(1.0-eccen2*sin(this->sl)*sin(this->sl) );
  this->tnaught  = tan(M_PI_4 - this->sl/2.) /
           pow(  ((1.0 - eccen*sin(this->sl))/(1.0+eccen*sin(this->sl))), eccen/2.);

  ijpt f;
  f.i = 0; f.j = 0;
  this->first_longitude = (this->locate(f)).lon;


  this->grid = new T[this->nx*this->ny] ;
  if (this->grid == (T *) NULL) { cout << "Failed to new in osisaf_north(void)\n";
    cout.flush(); }

  return;
}


int main(int argc, char *argv[]) {
  //osisaf_north<float> nh, lat, lon;
  osisaf_south<float> sh, lat, lon;
  ijpt loc;
  latpt llx, lly;

  // Read in netcdf information from osisaf
  float *x;
  int ncid, varid;
  int retval;
  x = (float*) malloc(sizeof(float)*sh.xpoints()*sh.ypoints());

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
  enter(sh, x);


  printf("%f %f\n",lon.gridmax(), lon.gridmin() );
  printf("%f %f\n",lat.gridmax(), lat.gridmin() );
  printf("%f %f\n",sh.gridmax(), sh.gridmin() );

  loc.i = sh.xpoints()/2;
  for (loc.j = 0; loc.j < sh.ypoints(); loc.j++ ) {
    llx = sh.locate(loc);
    if (llx.lon > 180.) {llx.lon -= 360.;}
    lly.lat = lat[loc];
    lly.lon = lon[loc];
    printf("%d %f %f %f  %f %f %f\n", loc.j, llx.lat, lly.lat, lly.lat-llx.lat, llx.lon, lly.lon, lly.lon-llx.lon);
  }

  return 0;
}
