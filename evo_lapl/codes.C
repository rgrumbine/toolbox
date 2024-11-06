
#include "grid_math.h"
#include "ncepgrids.h"

//RG: Doesn't need to consider mask
void laplacean(grid2<double> &x, grid2<double> &lapl, double &delta_max, double &rmse) {
  ijpt loc, ip, jp, im, jm;
  ijpt jp2, jp3;
  ijpt ip2, ip3, im2, im3;

  lapl.set((double)0.);

  for (loc.j = 1; loc.j < x.ypoints()-1; loc.j++) {
    ip.j = loc.j;
    im.j = loc.j;
    jp.j = loc.j+1;
    jm.j = loc.j-1;
    for (loc.i = 1; loc.i < x.xpoints() - 1 ; loc.i++) {
      jp.i = loc.i;
      jm.i = loc.i;
      ip.i = loc.i+1;
      im.i = loc.i-1;
      lapl[loc] = -4.*x[loc] + x[ip] + x[im] + x[jp] + x[jm];
    }
  }
  // edges
  loc.j = 0;
  ip.j = loc.j;
  im.j = loc.j;
  jp.j = loc.j + 1;
  jp2.j = loc.j + 2;
  jp3.j = loc.j + 3;
  for (loc.i = 1; loc.i < x.xpoints() - 1 ; loc.i++) {
    ip.i = loc.i+1;
    im.i = loc.i-1;
    // https://www.dam.brown.edu/people/alcyew/handouts/numdiff.pdf
    jp.i = loc.i; jp2.i = loc.i; jp3.i = loc.i; 
    lapl[loc] = (x[ip] - 2.*x[loc] + x[im]) + (2.*x[loc] - 5.*x[jp] + 4.*x[jp2] - x[jp3]);
  }
  loc.i = 0;
  ip.i = loc.i + 1;
  ip2.i = loc.i + 2;
  ip3.i = loc.i + 3;
  jp.i = loc.i;
  jm.i = loc.i;
//  for (loc.j = 1; loc.j < x.ypoints() - 1 ; loc.j++) {
//    jp.j = loc.j + 1;
//    jm.j = loc.j - 1;
//    ip.j = loc.j; ip2.j = loc.j; ip3.j = loc.j;
//    lapl[loc] = (x[jp] - 2.*x[loc] + x[jm]) + (2.*x[loc] - 5.*x[ip] + 4.*x[ip2] - x[ip3]);
//  }

  loc.i = x.xpoints() - 1;
  im.i = loc.i - 1;
  im2.i = loc.i - 2;
  im3.i = loc.i - 3;
  jp.i = loc.i;
  jm.i = loc.i;
  for (loc.j = 1; loc.j < x.ypoints() - 1 ; loc.j++) {
    jp.j = loc.j + 1;
    jm.j = loc.j - 1;
    im.j = loc.j; im2.j = loc.j; im3.j = loc.j;
    lapl[loc] = (x[jp] - 2.*x[loc] + x[jm]) + (2.*x[loc] - 5.*x[im] + 4.*x[im2] - x[im3]);
  }

  //debug: printf("lapl %f %f\n", lapl.gridmax(), lapl.gridmin() );

  delta_max = max(fabs(lapl.gridmax()), fabs(lapl.gridmin()) );
  rmse = lapl.rms();

  float ratio = 40.;
  int count = 0;
  for (loc.j = 0; loc.j < x.ypoints() - 1 ; loc.j++) {
    for (loc.i = 0; loc.i < x.xpoints() - 1 ; loc.i++) {
      if (lapl[loc] < -ratio*rmse || lapl[loc] > ratio*rmse) {
      //if (lapl[loc] < -59. || lapl[loc] > 59.) {
        count += 1;
	printf("%d %d %f %f\n",loc.i, loc.j, x[loc], lapl[loc]);
      }
    }
  }
  printf("count = %d\n",count);
  fflush(stdout);
  
}

//RG: Work with mask:
// laplacean has been computed
void sor(grid2<double> &x, grid2<double> &mask, grid2<double> &lapl, double &weight) {
  ijpt loc, ip, jp, im, jm;
  //grid2<double> tmp(x.xpoints(), x.ypoints() );
  //tmp = x;

  for (loc.j = 0; loc.j < x.ypoints()  ; loc.j++) {
  for (loc.i = 0; loc.i < x.xpoints()  ; loc.i++) {
    if (mask[loc] == 1.) {
      x[loc] += lapl[loc]/4. * weight;
    }
  }
  }
  
  return;
}

#define GRIDTYPE global_ice
int main(void) {
// read in sst
// read in land mask, set pts to 1 on land
  GRIDTYPE<double> x, mask, lapl;
  GRIDTYPE<float> sstin;
  GRIDTYPE<unsigned char> maskin;
  double weight = 0.99, toler = 1.e-9; 
  double rmse, delta_max;
  FILE *fin;
  ijpt loc;

  //fin = fopen("seaice_gland5min", "r");
  fin = fopen("seaice_newland", "r");
  maskin.binin(fin);
  fclose(fin);

  //fin = fopen("sst","r");
  sstin.set(30.0);
  //fclose(fin);

  for (loc.j = 0; loc.j < x.ypoints()  ; loc.j++) {
  for (loc.i = 0; loc.i < x.xpoints()  ; loc.i++) {
    if (maskin[loc] == 157) {
         x[loc] = 0.;
      mask[loc] = 1.;
    }
    else {
         x[loc] = sstin[loc];
      mask[loc] = 0.;
    }
  }
  }

  laplacean(x, lapl, delta_max, rmse);
  printf("delta max, rmse: %e %e\n",delta_max, rmse);

  palette<unsigned char> gg(19, 65);
  char fname[90];
  int iter = 0;
  GRIDTYPE<double> tmp;

  while (delta_max > toler && iter < 500*10 ) {
    sor(x, mask, lapl, weight);
    laplacean(x, lapl, delta_max, rmse);
    printf("%d delta max, rmse: %e %e\n",iter, delta_max, rmse);
    iter += 1;

    if ((iter % 500) == 0) {
      snprintf(fname, 90, "lapl%d.xpm",iter);
      tmp = lapl; tmp.scale();
      tmp.xpm(fname, 7, gg);
      snprintf(fname, 90, "sst%d.xpm",iter);
      tmp = x; tmp.scale();
      tmp.xpm(fname, 7, gg);
    }

  }
  
  return 0;
}
