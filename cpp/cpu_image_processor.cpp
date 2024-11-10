


#include <vector>
#include <numeric>
#include <algorithm>
#include <omp.h>
#include <iostream>
#include <cstddef> // For size_t
#include "cpu_image_processor.h"


#ifndef CPU_IMAGE_PROCESSOR_H
#define CPU_IMAGE_PROCESSOR_H

#ifdef _WIN32
#define DELLEXPORT extern "C" __declspec(dllexport)
#else
#define DELLEXPORT extern "C" __attribute__((visibility("default")))
#endif

// Function declarations
DELLEXPORT void run_cpu_filter(float* out, const float* in, size_t Y, size_t X);

#endif // CPU_IMAGE_PROCESSOR_H


void vmf_cpu(float* out, const float* in, size_t Y, size_t X)
{
    float vectR[9], vectG[9], vectB[9], alphas[9];
    const unsigned int nthreads = 2;

    for (int row = 1; row < Y - 1; row++) {
#pragma omp parallel for num_threads(nthreads) shared(out, in, X, row ) private (vectR, vectG, vectB, alphas) schedule(static)
        for (int col = 1; col < X - 1; col++) {
            ImageUtils::getWindow(vectR, vectG, vectB, in, row, col, X);

            std::vector<float> alphaValues = ImageUtils::getAlphaVmf(vectR, vectG, vectB);
            //std::vector<float> alphaValues = calculateAlphaValuesNewSIMD(vectR, vectG, vectB);

            std::vector<int> positions(9);
            std::iota(positions.begin(), positions.end(), 0);

            //std::sort(positions.begin(), positions.end(), [&alphaValues](int i, int j) {return alphaValues[i] < alphaValues[j];});
            //selectionSort(positions, alphaValues);
            ImageUtils::selectionSort(positions, alphaValues);

            out[(row * X + col) * 3 + 0] = vectR[positions[0]];
            out[(row * X + col) * 3 + 1] = vectG[positions[0]];
            out[(row * X + col) * 3 + 2] = vectB[positions[0]];
        }
    }
}
DELLEXPORT void run_cpu_filter(float* out, const float* in, size_t Y, size_t X) {
    vmf_cpu(out, in, Y, X);
}
