#include<vector>
#include <cmath>
#include <omp.h>

class ImageUtils {
public:
    static inline void getWindow(float* R, float* G, float* B, const float* img, int row, int col, size_t X);
    static inline float getL1(float r1, float r2, float g1, float g2, float b1, float b2);
    static inline std::vector<float> getAlphaVmf(const float* vectR, const float* vectG, const float* vectB);
    static inline void selectionSort(std::vector<int>& positions, const std::vector<float>& alphaValues);
};


inline void ImageUtils::getWindow(float* R, float* G, float* B, const float* img, int row, int col, size_t X) {
    constexpr int windowSize = 3;
    unsigned int F = 0;
    int index = 0;
    for (int i = -1; i <= 1; i++) {
        for (int j = -1; j <= 1; j++) {
            index = (row + i) * static_cast<int>(X) + (col + j);
            R[F] = img[index * 3 + 0];
            G[F] = img[index * 3 + 1];
            B[F] = img[index * 3 + 2];
            F++;
        }
    }
}

inline float ImageUtils::getL1(float r1, float r2, float g1, float g2, float b1, float b2) {
    return std::abs(r1 - r2) + std::abs(g1 - g2) + std::abs(b1 - b2);
}

inline std::vector<float> ImageUtils::getAlphaVmf(const float* vectR, const float* vectG, const float* vectB) {
    std::vector<float> alpha_values(9, 0.0f);

    for (unsigned int F = 0; F <= 8; F++) {
        for (unsigned int x = F + 1; x <= 8; x++) {
            float disteucl = getL1(vectR[F], vectR[x], vectG[F], vectG[x], vectB[F], vectB[x]);
            alpha_values[F] += disteucl;
            alpha_values[x] += disteucl;
        }
    }
    return alpha_values;
}

inline void ImageUtils::selectionSort(std::vector<int>& positions, const std::vector<float>& alphaValues) {
    for (size_t i = 0; i < positions.size() - 1; ++i) {
        size_t minIndex = i;
        for (size_t j = i + 1; j < positions.size(); ++j) {
            if (alphaValues[positions[j]] < alphaValues[positions[minIndex]]) {
                minIndex = j;
            }
        }
        std::swap(positions[i], positions[minIndex]);
    }
}

