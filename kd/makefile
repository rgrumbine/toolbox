all : main rtofs_grid

main : main.o kd.o
	gfortran main.o kd.o -o $(@)

rtofs_grid : main_rtofs.o kd.o
	gfortran main_rtofs.o kd.o -o $(@)

main.o : kd.o
main_rtofs.o : kd.o

%.o :%.f90
	gfortran -c -O2 $<

clean :
	rm *.o *.mod
