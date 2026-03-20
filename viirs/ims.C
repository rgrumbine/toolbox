//grid  1554 1 89.875 129.54166666666666 100.0 0.0 1

#include "ncepgrids.h"

int main(int argc, char *argv[]) {
  ims4km<float> x;
  latpt ll;
  fijpt floc;
  FILE *fin;
  int i,j;
  float mean, sigma;
  float tmean, tsigma;
  int count;

  fin = fopen(argv[1],"r");
  while (!feof(fin)) {
    fscanf(fin, "%d %d %f %f %f %f %f %f %d\n",&i, &j, &ll.lat, &ll.lon, &mean, &sigma, &tmean, &tsigma, &count);

    if (ll.lat > 20) {
      floc = x.locate(ll);
      printf("%d %d %f %f %f %f %f %f %d\n",(int) (0.5+floc.i), (int) (0.5+floc.j), 
              ll.lat, ll.lon, mean, sigma, tmean, tsigma, count);
    }
    else {
      floc.i = -1;
      floc.j = -1;
      printf("%d %d %f %f %f %f %f %f %d\n",(int) (floc.i), (int) (floc.j), 
              ll.lat, ll.lon, mean, sigma, tmean, tsigma, count);
    }
  }

  return 0;
}
