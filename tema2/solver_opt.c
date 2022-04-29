/*
 * Tema 2 ASC
 * 2022 Spring
 */
#include "utils.h"

/*
 * Add your optimized implementation here
 */
extern inline void transpose_matrix(int N, double* transposed, double *A) {
	for (int i = 0; i < N; i++) {
        double *src = &A[i * N];
        double *dst = &transposed[i];
        for (int j = 0; j < N; j++) {
            *dst = *src;
            src++;
            dst += N;
        }
    }
}


extern inline void multiply_matrix_with_transposed(int N, double* res, double* A, double* B) {
    for (int i = 0; i < N; i++) {
        for (int k = 0; k < N; k++) {
            register double tmp_elem = A[i * N + k];
            for (int j = 0; j <= i; j += 4) {
                res[i * N + j] += tmp_elem * B[k * N + j];
                res[i * N + j + 1] += tmp_elem * B[k * N + j + 1];
                res[i * N + j + 2] += tmp_elem * B[k * N + j + 2];
                res[i * N + j + 3] += tmp_elem * B[k * N + j + 3];
            }
        }
    }

    for (int i = 0; i < N; i++) {
        double *src = &res[i * N];
        double *dst = &res[i];
        for (int j = 0; j < i; j++) {
            *dst = *src;
            src++;
            dst += N;
        }
    }
}

extern inline void multiply_upper_triangular_matrix(int N, double* res, double* A, double* upper_triangular) {
    for (int i = 0; i < N; i++) {
        for (int k = 0; k < N; k++) {
            register double tmp_elem = A[i * N + k];
            for (int j = k; j < N; j++) {
                res[i * N + j] += tmp_elem * upper_triangular[k * N + j];
            }
        }
    }
}

extern inline void multiply_lower_triangular_matrix(int N, double* res, double* A, double* lower_triangular) {
    for (int i = 0; i < N; i++) {
        for (int k = 0; k < N; k++) {
            register double tmp_elem = A[i * N + k];
            for (int j = 0; j <= k; j++) {
                res[i * N + j] += tmp_elem * lower_triangular[k * N + j];
            }
        }
    }
}

extern inline void add_matrix(int N, double* dst_matrix, double* src_matrix) {
    for (int i = 0; i < N; i++) {
        unsigned int matrix_index = i * N;
        double *src = &src_matrix[matrix_index];
        double *dst = &dst_matrix[matrix_index];
        for (int j = 0; j < N; j++) {
            *dst += *src;
            dst++;
            src++;
        }
    }
}

double* my_solver(int N, double *A, double* B) {
	double* first_part = calloc(N * N, sizeof(double));
    double* res = calloc(N * N, sizeof(double));
    double* transposed_A = calloc(N * N, sizeof(double));
    transpose_matrix(N, transposed_A, A);
    multiply_upper_triangular_matrix(N, first_part, B, A);
    multiply_lower_triangular_matrix(N, res, first_part, transposed_A);

    double* second_part = calloc(N * N, sizeof(double));
    double* transposed_B = calloc(N * N, sizeof(double));
    transpose_matrix(N, transposed_B, B);
    multiply_matrix_with_transposed(N, second_part, transposed_B, B);

    add_matrix(N, res, second_part);

    free(first_part);
    free(second_part);
    free(transposed_A);
    free(transposed_B);
	return res;
}