/*
 * Tema 2 ASC
 * 2022 Spring
 */
#include "utils.h"
#include "cblas.h"
#include <stdio.h>
#include <string.h>

/* 
 * Add your BLAS implementation here
 */
double* my_solver(int N, double *A, double *B) {
    double* copyB = calloc(N * N, sizeof(double));
    for (int i = 0; i < N * N; i++) {
        copyB[i] = B[i];
    }

    cblas_dtrmm(CblasRowMajor, CblasRight, CblasUpper, CblasNoTrans, CblasNonUnit, N, N, 1.0, A, N, B, N);
    cblas_dtrmm(CblasRowMajor, CblasRight, CblasUpper, CblasTrans, CblasNonUnit, N, N, 1.0, A, N, B, N);
	cblas_dgemm(CblasRowMajor, CblasTrans, CblasNoTrans, N, N, N, 1.0, copyB, N, copyB, N, 1.0, B, N);

    double* res = calloc(N * N, sizeof(double));
    for (int i = 0; i < N * N; i++) {
        res[i] = B[i];
    }
    
    free(copyB);
	return res;
}
