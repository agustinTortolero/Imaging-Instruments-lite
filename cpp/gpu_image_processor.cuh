#include "cuda_runtime.h"
#include <math_functions.h>//fabsf

class DeviceImageProcessor {
public:
    __forceinline__ __device__ void getWindow(float* R, float* G, float* B, const float* img, int Row, int Col, size_t X);
    __forceinline__ __device__ float getL1(float r1, float r2, float g1, float g2, float b1, float b2);
    __forceinline__ __device__ void getAlphaVmf(float* vectR, float* vectG, float* vectB, float* alpha_values, const unsigned int n_pixels);
    __forceinline__ __device__ void selectionSort(int* positions, const float* alphaValues, int n);
};


