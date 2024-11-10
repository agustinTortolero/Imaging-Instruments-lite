#include "device_launch_parameters.h"
#include "cuda_runtime.h"

#include <iostream>

#include "gpu_image_processor.cuh"

#define DELLEXPORT extern "C" __declspec(dllexport)


__forceinline__ __device__ void DeviceImageProcessor::getWindow(float* R, float* G, float* B, const float* img, int Row, int Col, size_t X) {
    const int n_pixels = 9;
    const int window_pos = n_pixels / 9;
    unsigned int index = 0;
    unsigned c = 0;
    for (int i = -window_pos; i <= window_pos; i++) {
        for (int j = -window_pos; j <= window_pos; j++) {
            index = (Row + i) * X + (Col + j);
            R[c] = static_cast<float>(img[index * 3 + 0]);
            G[c] = static_cast<float>(img[index * 3 + 1]);
            B[c] = static_cast<float>(img[index * 3 + 2]);
            c++;
        }
    }
}


__forceinline__ __device__ float DeviceImageProcessor::getL1(float r1, float r2, float g1, float g2, float b1, float b2) {
    return fabsf(r1 - r2) + fabsf(g1 - g2) + fabsf(b1 - b2);
}


__forceinline__ __device__ void DeviceImageProcessor::getAlphaVmf(float* vectR, float* vectG, float* vectB, float* alpha_values, const unsigned int n_pixels) {
    float alpha = 0;

    for (unsigned int a = 0; a < n_pixels; a++) {
        for (unsigned int b = 0; b < n_pixels; b++) {
            alpha += getL1(vectR[a], vectR[b], vectG[a], vectG[b], vectB[a], vectB[b]);
        }

        alpha_values[a] = alpha;
        alpha = 0;
    }
}
__forceinline__ __device__ void DeviceImageProcessor::selectionSort(int* positions, const float* alphaValues, int n) {
    for (int i = 0; i < n - 1; ++i) {
        int minIdx = i;
        for (int j = i + 1; j < n; ++j) {
            if (alphaValues[positions[j]] < alphaValues[positions[minIdx]]) {
                minIdx = j;
            }
        }
        // Swap positions[i] and positions[minIdx]
        int temp = positions[i];
        positions[i] = positions[minIdx];
        positions[minIdx] = temp;
    }
}


__global__ void vmf_gpu(float* out, const float* in, size_t Y, size_t X) {
    int Row = blockIdx.y * blockDim.y + threadIdx.y;
    int Col = blockIdx.x * blockDim.x + threadIdx.x;

    DeviceImageProcessor processor;

    float vectR[9], vectG[9], vectB[9];
    float alphas[9];
    int positions[9];

    const unsigned int n_pixels = 9;
    unsigned int output_pixel_index = 0;

    if ((Row > 1) && (Col > 1) && (Row < Y - 1) && (Col < X - 1)) {
        processor.getWindow(vectR, vectG, vectB, in, Row, Col, X);
        processor.getAlphaVmf(vectR, vectG, vectB, alphas, n_pixels);

        // Necessary for selectionSort
        for (int i = 0; i < n_pixels; ++i) {
            positions[i] = i;
        }
        processor.selectionSort(positions, alphas, n_pixels);

        unsigned int output_pixel_index = positions[0];

        // Set the output pixel values
        out[(Row * X + Col) * 3 + 0] = static_cast<unsigned char>(vectR[output_pixel_index]);
        out[(Row * X + Col) * 3 + 1] = static_cast<unsigned char>(vectG[output_pixel_index]);
        out[(Row * X + Col) * 3 + 2] = static_cast<unsigned char>(vectB[output_pixel_index]);
    }
}


DELLEXPORT void run_gpu_filter(float* img_filtered, const float* img_noisy, size_t Y, size_t X) {

    cudaError_t cudaStatus;
    int device_count = 0;
    cudaStatus = cudaGetDeviceCount(&device_count);
    if (cudaStatus != cudaSuccess || device_count == 0) {
        goto Error;
    }

    float* device_img_noisy = nullptr;
    float* device_img_filtered = nullptr;

    size_t img_size = Y * X * sizeof(float) * 3;

    cudaStatus = cudaMalloc((void**)&device_img_noisy, img_size);
    if (cudaStatus != cudaSuccess) {
        std::cerr << "cudaMalloc failed!" << std::endl;
        goto Error;
    }
    cudaStatus = cudaMalloc((void**)&device_img_filtered, img_size);
    if (cudaStatus != cudaSuccess) {
        std::cerr << "cudaMalloc failed!" << std::endl;
        goto Error;
    }
    cudaStatus = cudaMemcpy(device_img_noisy, img_noisy, img_size, cudaMemcpyHostToDevice);
    if (cudaStatus != cudaSuccess) {
        std::cerr << "cudaMemcpy failed!" << std::endl;
        goto Error;
    }

    int nHilosporBloque = 8;
    dim3 nThreads(nHilosporBloque, nHilosporBloque, 1);
    dim3 nBloques((X / nHilosporBloque) + 1, (Y / nHilosporBloque) + 1, 1);


    vmf_gpu << <nBloques, nThreads >> > (device_img_filtered, device_img_noisy, Y, X);


    cudaStatus = cudaGetLastError();
    if (cudaStatus != cudaSuccess) {
        std::cerr << "Kernel launch failed: " << cudaGetErrorString(cudaStatus) << std::endl;
        goto Error;
    }
    cudaStatus = cudaDeviceSynchronize();
    if (cudaStatus != cudaSuccess) {
        std::cerr << "cudaDeviceSynchronize returned error code " << cudaStatus << " after launching kernel!" << std::endl;
        goto Error;
    }
    cudaStatus = cudaMemcpy(img_filtered, device_img_filtered, img_size, cudaMemcpyDeviceToHost);
    if (cudaStatus != cudaSuccess) {
        std::cerr << "cudaMemcpy failed!" << std::endl;
        goto Error;
    }

    cudaFree(device_img_noisy);
    cudaFree(device_img_filtered);


Error:
    cudaFree(device_img_noisy);
    cudaFree(device_img_filtered);
}
