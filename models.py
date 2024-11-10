import os
import cv2
import numpy as np
import random
from pathlib import Path

try:
    from numba import jit, prange
    numba_available = True
except ImportError:
    numba_available = False


class ImageModel:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def open_image(self, file_path):
    # Ensure the file path is in the correct format
        file_path = Path(file_path)
    
        if not file_path.exists():
            print("Error", "File path does not exist. Please try another file.")
            return None

    # Convert the file path to a string and handle special characters
        file_path_str = str(file_path)

    # Open the image with OpenCV
        cv2_img = cv2.imdecode(np.fromfile(file_path_str, dtype=np.uint8), cv2.IMREAD_COLOR)
    
    # Check if the image was loaded successfully
        if cv2_img is None:
            print("Error", "Failed to load image. Please try another file.")
            return None
    
    # Convert the image to RGB format
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    
        return cv2_img


    def apply_sobel_edge(self, cv2_img):
        if cv2_img is None:
            return None
        gray_image = cv2.cvtColor(cv2_img, cv2.COLOR_RGB2GRAY)
        sobel_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
        sobel_edges = np.sqrt(sobel_x**2 + sobel_y**2)
        sobel_edges = cv2.normalize(sobel_edges, None, 0, 255, cv2.NORM_MINMAX)
        sobel_edges = np.uint8(sobel_edges)
        return sobel_edges
    
    def histogram_equalization_hsi(self, cv2_img):
        hsi_image = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)
        h, s, i = cv2.split(hsi_image)
        equalized_i = cv2.equalizeHist(i)
        equalized_hsi_image = cv2.merge([h, s, equalized_i])
        equalized_image = cv2.cvtColor(equalized_hsi_image, cv2.COLOR_HSV2BGR)
        original_hist = [cv2.calcHist([cv2_img], [i], None, [256], [0, 256]) for i in range(3)]
        equalized_hist = [cv2.calcHist([equalized_image], [i], None, [256], [0, 256]) for i in range(3)]
        return equalized_image, original_hist, equalized_hist
    
    def pencil_sketch_effect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        inv_gray = 255 - gray
        blurred = cv2.GaussianBlur(inv_gray, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blurred, scale=256)
        return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    
    def cartoon_effect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
        cartoon = cv2.medianBlur(blur, 7)
        edges = cv2.adaptiveThreshold(cartoon, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, blockSize=9, C=2)
        result = cv2.bitwise_and(frame, frame, mask=edges)
        return result
    
    
    def old_movie_distortion(self, frame):
        noise = np.zeros_like(frame)
        cv2.randn(noise, 25, 10)
        frame_with_noise = cv2.add(frame, noise)
        grain = np.zeros_like(frame)
        cv2.randn(grain, 50, 10)
        frame_with_grain = cv2.add(frame_with_noise, grain)
        alpha = 1.5
        beta = 50
        adjusted_frame = cv2.convertScaleAbs(frame_with_grain, alpha=alpha, beta=beta)
        noise_intensity = 5
        blurred_frame = cv2.blur(adjusted_frame, (noise_intensity, noise_intensity))
        if random.randint(1, 15) == 1:
            height, width, _ = frame.shape
            num_pixels = int(height * width * 0.005)
            for _ in range(num_pixels):
                y = random.randint(0, height - 1)
                x = random.randint(0, width - 1)
                if random.random() < 0.5:
                    blurred_frame[y, x] = 5
                else:
                    blurred_frame[y, x] = 240
        return blurred_frame
    
    def apply_noise(self, img, noise_type, noise_density):
        if noise_type == "Salt and Pepper":
            noisy_image = self.salt_pepper(img, noise_density / 100)
        elif noise_type == "Gaussian":
            noisy_image = self.add_gaussian_noise_color(img, noise_density)
        else:
            raise ValueError("Unsupported noise type selected.")
    
    # Debugging statements
        if noisy_image is None:
            raise ValueError("The noisy image is None.")
        if not isinstance(noisy_image, np.ndarray):
            raise ValueError(f"Expected numpy array, but got {type(noisy_image)}.")
        return noisy_image

    @staticmethod
    def salt_pepper(img, p):
        row, col, channels = img.shape
        npixels = row * col
        number_of_pixels = round(npixels * p / 2)  # Correct calculation
        
                # Debug prints
        print(f"Image shape: (row={row}, col={col}, channels={channels})")
        print(f"Total number of pixels: {npixels}")
        print(f"Number of pixels to be affected: {number_of_pixels} (for p={p})")


        if numba_available:
            return ImageModel.salt_pepper_numba(img, p, number_of_pixels, row, col, channels)
        else:
            return ImageModel.salt_pepper_plain(img, p, number_of_pixels, row, col, channels)

    @staticmethod
    def salt_pepper_plain(img, p, number_of_pixels, row, col, channels):
        print("running on cpu")
        # Add salt noise
        for _ in range(number_of_pixels):
            y_coord = np.random.randint(0, row)
            x_coord = np.random.randint(0, col)
            channel = np.random.randint(0, channels)
            img[y_coord, x_coord, channel] = 255
        # Add pepper noise
        for _ in range(number_of_pixels):
            y_coord = np.random.randint(0, row)
            x_coord = np.random.randint(0, col)
            channel = np.random.randint(0, channels)
            img[y_coord, x_coord, channel] = 0
        print("finish salt_pepper")
        return img

    @staticmethod
    @jit(nopython=True)
    def salt_pepper_numba(img, p, number_of_pixels, row, col, channels):
        print("running on gpu")
        # Add salt noise
        for _ in range(number_of_pixels):
            y_coord = np.random.randint(0, row)
            x_coord = np.random.randint(0, col)
            channel = np.random.randint(0, channels)
            img[y_coord, x_coord, channel] = 255
        # Add pepper noise
        for _ in range(number_of_pixels):
            y_coord = np.random.randint(0, row)
            x_coord = np.random.randint(0, col)
            channel = np.random.randint(0, channels)
            img[y_coord, x_coord, channel] = 0
        print("finish salt_pepper")
        return img
    
    def add_gaussian_noise_color(self, img, sigma=20):
        row, col, channels = img.shape
        gauss = np.random.normal(0, sigma, (row, col, channels))
        noisy_img = img + gauss
        noisy_img = np.clip(noisy_img, 0, 255)
        noisy_img = noisy_img.astype(np.uint8)
        return noisy_img
    
    def adjust_contrast_brightness(self, image, alpha, beta):
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    def adjust_gamma(self, image, gamma):
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(image, table)

    def pixelate(self, image, pixelation_level):
        height, width = image.shape[:2]
        small_width = width // pixelation_level
        small_height = height // pixelation_level
        temp_image = cv2.resize(image, (small_width, small_height), interpolation=cv2.INTER_LINEAR)
        pixelated_image = cv2.resize(temp_image, (width, height), interpolation=cv2.INTER_NEAREST)
        return pixelated_image

    def pixelate_faces(self, image, pixelation_level=10):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in faces:
            face_region = image[y:y+h, x:x+w]
            pixelated_face = self.pixelate(face_region, pixelation_level)
            image[y:y+h, x:x+w] = pixelated_face
        return image
