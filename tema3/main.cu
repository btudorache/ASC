#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <fstream>
#include <vector>
#include <cmath>

#define DIM_BLOCK_SIZE 1024
#define DEGREE_TO_RADIANS 0.01745329252f
#define MAX_INPUT_SIZE 500000

#define DIE(assertion, call_description)                    \
do {                                                        \
    if (assertion) {                                        \
            fprintf(stderr, "(%d): ",                       \
                            __LINE__);                      \
            perror(call_description);                       \
            exit(EXIT_FAILURE);                             \
    }                                                       \
} while(0);


__global__ void calculate_population(register float *lats, 
                                     register float *longs,
                                     register int *pops, 
                                     register int *results,
                                     register float km_range, 
                                     register size_t n) {
    register float phi1, phi2, theta1, theta2, cs, distance, index_lat, index_long, used_lat, used_long;
    register int i, curr_block_index, curr_thread_block_index, curr_pop, used_pop;
    register size_t index = threadIdx.x + blockDim.x * blockIdx.x;

    __shared__ float cached_lats[DIM_BLOCK_SIZE];
    __shared__ float cached_longs[DIM_BLOCK_SIZE];
    __shared__ int cached_pops[DIM_BLOCK_SIZE];
    cached_lats[threadIdx.x] = lats[index];
    cached_longs[threadIdx.x] = longs[index];
    cached_pops[threadIdx.x] = pops[index];

    __syncthreads();

  	if (index < n) {
        index_lat = lats[index];
        index_long = longs[index];
        curr_pop = pops[index];

        for (i = index + 1; i < n; i++) {
            curr_block_index = i / blockDim.x;
            curr_thread_block_index = i % blockDim.x;
            if (blockIdx.x == curr_block_index) {
                used_lat = cached_lats[curr_thread_block_index];
                used_long = cached_longs[curr_thread_block_index];
                used_pop = cached_pops[curr_thread_block_index];
            } else {
                used_lat = lats[i];
                used_long = longs[i];
                used_pop = pops[i];
            }

            phi1 = (90.f - index_lat) * DEGREE_TO_RADIANS;
            phi2 = (90.f - used_lat) * DEGREE_TO_RADIANS;

            theta1 = index_long * DEGREE_TO_RADIANS;
            theta2 = used_long * DEGREE_TO_RADIANS;

            cs = sin(phi1) * sin(phi2) * cos(theta1 - theta2) + cos(phi1) * cos(phi2);
            if (cs > 1) {
                cs = 1;
            } else if (cs < -1) {
                cs = -1;
            }

            distance = 6371.f * acos(cs);

            if (distance < km_range) {
                atomicAdd(&results[index], used_pop);
                atomicAdd(&results[i], curr_pop);
            }
        }
    }
}

int main(int argc, char** argv) {
    DIE( argc == 1,
         "./accpop <kmrange1> <file1in> <file1out> ...");
    DIE( (argc - 1) % 3 != 0,
         "./accpop <kmrange1> <file1in> <file1out> ...");

    int* results = NULL;

    float* device_latitudes = 0;
    float* device_longitudes = 0;
    int* device_populations = 0;
    int* device_results = 0;

    unsigned char allocated = 0;

    for(int argcID = 1; argcID < argc; argcID += 3) {
        float km_range = atof(argv[argcID]);

        std::string geon;
        float lat;
        float lon;
        int pop;

        std::vector<float> lats;
        std::vector<float> longs;
        std::vector<int> pops;

        std::ifstream ifs(argv[argcID + 1]);
        std::ofstream ofs(argv[argcID + 2]);

        while(ifs >> geon >> lat >> lon >> pop) {
            lats.push_back(lat);
            longs.push_back(lon);
            pops.push_back(pop);
        }

        allocated = 1;
        int n = (int)pops.size();

        const size_t block_size = DIM_BLOCK_SIZE;
        size_t num_blocks = n / block_size;

        if (n % DIM_BLOCK_SIZE != 0) {
            num_blocks++;
        }

        if (n > MAX_INPUT_SIZE) {
            continue;
        }

        int float_num_bytes = n * sizeof(float);
        int int_num_bytes = n * sizeof(int);

        results = (int *)malloc(int_num_bytes);

        cudaMalloc((void **) &device_latitudes, float_num_bytes);
	    cudaMalloc((void **) &device_longitudes, float_num_bytes);
        cudaMalloc((void **) &device_populations, int_num_bytes);
        cudaMalloc((void **) &device_results, int_num_bytes);

        cudaMemcpy(device_latitudes, lats.data(), float_num_bytes, cudaMemcpyHostToDevice);
        cudaMemcpy(device_longitudes, longs.data(), float_num_bytes, cudaMemcpyHostToDevice);
        cudaMemcpy(device_populations, pops.data(), int_num_bytes, cudaMemcpyHostToDevice);
        cudaMemcpy(device_results, pops.data(), int_num_bytes, cudaMemcpyHostToDevice);

        calculate_population<<<num_blocks, block_size>>>(device_latitudes, device_longitudes, device_populations, device_results, km_range, n);

        cudaMemcpy(results, device_results, int_num_bytes, cudaMemcpyDeviceToHost);

        for (int i = 0; i < n; i++) {
            ofs << results[i] << "\n";
        }

        ifs.close();
        ofs.close();
    }

    if (allocated) {
        free(results);

        cudaFree(device_latitudes);
        cudaFree(device_longitudes);
        cudaFree(device_populations);
        cudaFree(device_results);
    }
}
