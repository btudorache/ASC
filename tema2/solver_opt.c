/*
 * Tema 2 ASC
 * 2022 Spring
 */
#include "utils.h"

/*
 * Add your optimized implementation here
 */
extern inline void transpose_matrix(register int N, register double* transposed, register double *A) {
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


extern inline void multiply_matrix_with_transposed(register int N, register double* res, register double* A, register double* B) {
    for (int i = 0; i < N; i++) {
        double *outer_a = &A[i * N];
        double *outer_res = &res[i * N];
        double *outer_b = &B[0];
        for (int k = 0; k < N; k++) {
            double *inner_b = outer_b;
            double *inner_res = outer_res;
            register double tmp_elem = A[i * N + k];
            for (int j = 0; j <= i; j += 4) {
                *inner_res += tmp_elem * *inner_b;
                inner_res++;
                inner_b++;

                *inner_res += tmp_elem * *inner_b;
                inner_res++;
                inner_b++;
                
                *inner_res += tmp_elem * *inner_b;
                inner_res++;
                inner_b++;

                *inner_res += tmp_elem * *inner_b;
                inner_res++;
                inner_b++;
            }
            outer_a++;
            outer_b += N;
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

extern inline void multiply_upper_triangular_matrix(register int N, register double* res, register double* A, register double* upper_triangular) {
    for (int i = 0; i < N; i++) {
        for (int k = 0; k < N; k++) {
            register double tmp_elem = A[i * N + k];
            for (int j = k; j < N; j++) {
                res[i * N + j] += tmp_elem * upper_triangular[k * N + j];
            }
        }
    }
}

extern inline void multiply_lower_triangular_matrix(register int N, register double* res, register double* A, register double* lower_triangular) {
    for (int i = 0; i < N; i++) {
        for (int k = 0; k < N; k++) {
            register double tmp_elem = A[i * N + k];
            for (int j = 0; j <= k; j++) {
                res[i * N + j] += tmp_elem * lower_triangular[k * N + j];
            }
        }
    }
}

extern inline void add_matrix(register int N, register double* dst_matrix, register double* src_matrix) {
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

double* my_solver(register int N, register double *A, register double* B) {
	register double* first_part = calloc(N * N, sizeof(double));
    register double* res = calloc(N * N, sizeof(double));
    register double* transposed_A = calloc(N * N, sizeof(double));
    transpose_matrix(N, transposed_A, A);
    multiply_upper_triangular_matrix(N, first_part, B, A);
    multiply_lower_triangular_matrix(N, res, first_part, transposed_A);

    register double* second_part = calloc(N * N, sizeof(double));
    register double* transposed_B = calloc(N * N, sizeof(double));
    transpose_matrix(N, transposed_B, B);
    multiply_matrix_with_transposed(N, second_part, transposed_B, B);

    add_matrix(N, res, second_part);

    free(first_part);
    free(second_part);
    free(transposed_A);
    free(transposed_B);
	return res;
}