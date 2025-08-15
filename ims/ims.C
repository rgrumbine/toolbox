#include "ncepgrids.h"

template<class T>
class ims4km : public psgrid<T> {
  public:
    ims4km();
};
template<class T>
ims4km<T>::ims4km() {
  this->nx = 6144;
  this->ny = 6144;
  this->dx = 4000.;
  this->dy = 4000.;
  this->slat = 60.0;  
  this->slon = -10.0;
  this->xorig = -(this->nx/2)*this->dx ;
  this->yorig = -(this->ny/2)*this->dy ;
  this->sgn   = 1.0;

  double eccen2 = parameters::eccen2;
  double eccen  = sqrt(eccen2);
  this->sl = this->slat / parameters::degrees_per_radian;
  this->cm = cos(this->sl)/ sqrt(1.0-eccen2*sin(this->sl)*sin(this->sl) );
  this->tnaught  = tan(M_PI_4 - this->sl/2.) /
           pow(  ((1.0 - eccen*sin(this->sl))/(1.0+eccen*sin(this->sl))), eccen/2.);

  ijpt f;
  f.i = 0; f.j = 0;
  this->first_longitude = (this->locate(f)).lon;

  this->grid = new T[this->nx*this->ny];
  if (this->grid == (T *) NULL) { cout << "Failed to new in ims_north(void)\n";
    cout.flush();}

  return ;
}


int main(void) {
  ims_north<float> x(96);
  ims4km<float> y;
  ijpt loc;
  latpt llx, lly;

  printf("%d %d\n",x.xpoints(), y.xpoints() );
  loc.i = x.xpoints()/2;
  for (loc.j = 0; loc.j < x.ypoints(); loc.j++ ) {
    llx = x.locate(loc);
    lly = y.locate(loc);
    printf("%d %f %f %f  %f %f %f\n", loc.j, llx.lat, lly.lat, lly.lat-llx.lat, llx.lon, lly.lon, lly.lon-llx.lon);
  }

  return 0;
}
