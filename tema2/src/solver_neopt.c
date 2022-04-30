/*
 * Tema 2 ASC
 * 2022 Spring
 */
#include "utils.h"

/*
 * Add your unoptimized implementation here
 */
void transpose_matrix(int N, double* transposed, double *A) {
	for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            transposed[i * N + j] = A[j * N + i];
        }
    }
}

void multiply_matrix_with_transposed(int N, double* res, double* A, double* B) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            for (int k = 0; k < N; k++) {
                res[i * N + j] += A[i * N + k] * B[k * N + j];
            }
        }
    }
}

void multiply_upper_triangular_matrix(int N, double* res, double* A, double* upper_triangular) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            for (int k = 0; k <= j; k++) {
                res[i * N + j] += A[i * N + k] * upper_triangular[k * N + j];
            }
        }
    }
}

void multiply_lower_triangular_matrix(int N, double* res, double* A, double* lower_triangular) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            for (int k = j; k < N; k++) {
                res[i * N + j] += A[i * N + k] * lower_triangular[k * N + j];
            }
        }
    }
}

void add_matrix(int N, double* dst_matrix, double* src_matrix) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            dst_matrix[i * N + j] += src_matrix[i * N + j];
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
