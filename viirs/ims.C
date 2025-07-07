//grid  1554 1 89.875 129.54166666666666 100.0 0.0 1
//grid  1564 1 89.875 130.37499999999997 100.0 0.0 1
//grid  1605 1 89.875 133.79166666666666 100.0 0.0 1
//grid  1617 1 89.875 134.79166666666666 100.0 0.0 1
//grid  1629 1 89.875 135.79166666666666 100.0 0.0 1
//grid  1657 1 89.875 138.12499999999997 100.0 0.0 1
//grid  1671 1 89.875 139.29166666666666 100.0 0.0 1
//grid  1685 1 89.875 140.45833333333331 100.0 0.0 1
//grid  1700 1 89.875 141.70833333333331 100.0 0.0 1
//grid  1710 1 89.875 142.54166666666666 100.0 0.0 1

#include "ncepgrids.h"

int main(int argc, char *argv[]) {
  ims4km<float> x;
  latpt ll;
  fijpt floc;
  FILE *fin;
  char name[90];
  int i,j;
  float mean, sigma;
  int count;

  fin = fopen(argv[1],"r");
  while (!feof(fin)) {
    fscanf(fin, "%d %d %f %f %f %f %d\n",&i, &j, &ll.lat, &ll.lon, &mean, &sigma, &count);
    //printf("%d %d %f %f\n",i,j,ll.lat, ll.lon);
    if (ll.lat > 20) {
      floc = x.locate(ll);
      printf("%d %d %f %f %f %f %d\n",(int) (0.5+floc.i), (int) (0.5+floc.j), 
              ll.lat, ll.lon, mean, sigma, count);
    }
  }

  return 0;
}
