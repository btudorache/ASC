all: gpu_sol

gpu_sol:
	nvcc -g -arch=sm_35 -rdc=true main.cu -o gpu_sol -O0

clean:
	rm -f gpu_sol *.o