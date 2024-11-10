import platform
import os
import subprocess

import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, StringVar, W, DISABLED

import numpy as np
import time
import ctypes as ct
from threading import Thread
import psutil
import numba.cuda
from PIL import Image , ImageTk
import cv2

from models import ImageModel
from views import *



class ImageController:
    def __init__(self, root,execution_mode ="CPU"):  
        self.root = root
        self.cv2_img = np.zeros((400, 400, 3), dtype=np.uint8) * 255  
        self.sobel_edges = None
        self.execution_mode = execution_mode
        self.view = ImageViewer(self.root, self)
        
        self.model = ImageModel()

        self.cuda_available = numba.cuda.is_available()

        
        self.lib = None
        self.lib= self.get_lib()
        
        self.selected_effect = None
        self.zoom_window = None

        self.original_photo_image = None
        self.sobel_photo_image = None
        
        self.view_adjust = None  
        self.view_noise = None 
        
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon-Imaging-instruments-lite.png')

        try:
            img = Image.open(icon_path)
            self.root.iconphoto(False, ImageTk.PhotoImage(img))
        except Exception as e:
            print(f"Error setting iconphoto: {e}")

        # Windows specific AppUserModelID setting
        if platform.system() == "Windows":
            myappid = 'imaging-instruments-lite'
            ct.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("BMP files", "*.bmp"), ("All files", "*.*")])
        if file_path:
        # Open the image
            self.cv2_img = self.model.open_image(file_path)
        # Check if the image was loaded successfully
            if self.cv2_img is None:
                messagebox.showerror("Error", "Failed to load image. Please try another file.")
                return
            
        # Check if the image has 3 color channels
            if self.cv2_img.ndim != 3 or self.cv2_img.shape[2] != 3:
                messagebox.showerror("Error", "Invalid image format. The image must have 3 color channels (RGB).")
                return 
            
        # Check the image dimensions
            height, width, _ = self.cv2_img.shape
            if width < 50 or height < 50:
                messagebox.showerror("Error", "The image is too small. Minimum dimensions are 50x50 pixels.")
                return
          
            if width > 6000 or height > 6000:
                messagebox.showerror("Error", "The image is too large. Maximum dimensions are 6000x6000 pixels.")
                return

            self.view.display_image(self.cv2_img)
                    
    def inspect(self):
        if self.cv2_img is not None:
            self.zoom_window = ZoomWindow(self.root, self.cv2_img)
            self.zoom_window.grab_set() 
            self.root.wait_window(self.zoom_window)
            
    def apply_sobel(self):
        if self.cv2_img is not None:
            self.sobel_edges = self.model.apply_sobel_edge(self.cv2_img)
            self.view_sobel = SobelView(self.root, self, self.cv2_img, self.sobel_edges)
                   
    def apply_gaussian_blur(self):
        if self.cv2_img is not None:
            self.gaussian_filtered = cv2.bilateralFilter(self.cv2_img, 15, 75, 75)
            self.view_gaussian = GaussianFilterView(self.root, self, self.cv2_img, self.gaussian_filtered)
        

    
    def apply_histogram_equalization(self):
        if self.cv2_img is not None:
            self.equalized_image, self.original_hist, self.equalized_hist = self.model.histogram_equalization_hsi(self.cv2_img)
            
            self.view_histeq = HistogramView(self.root, self,self.cv2_img, self.original_hist, self.equalized_image, self.equalized_hist)
            self.view_histeq.window.grab_set()
            self.root.wait_window(self.view_histeq.window)

    def apply_adjust(self):
        if self.cv2_img is not None:
            self.view_adjust = ImageAdjustmentView(self.root, self, self.cv2_img)
            self.view_adjust.window.grab_set()
            self.root.wait_window(self.view_adjust.window)
            
    def apply_noise(self, original_image_cv=None, noise_type=None, noise_density=None):
        if original_image_cv is None:
            if self.cv2_img is not None:
                self.view_noise = NoiseGeneratorView(self.root, self, Image.fromarray(self.cv2_img))
                self.view_noise.window.grab_set()  # Assuming `window` is defined in your NoiseGeneratorView
                self.root.wait_window(self.view_noise.window)
        else:
            # Create a copy of the original image to avoid modifying the original
            image_copy = original_image_cv.copy()
            if not isinstance(image_copy, np.ndarray):
                image_copy = np.array(image_copy)
                
            # Apply noise to the copy instead of the original image
            noisy_image = self.model.apply_noise(image_copy, noise_type, noise_density)

            if noisy_image is None:
                print("Error: The noisy image returned by the model is None.")
                return None

            if not isinstance(noisy_image, np.ndarray):
                print(f"Error: The noisy image is not a numpy array. Type: {type(noisy_image)}")
                return None

            # Convert the noisy image to PIL format
            noisy_image_pil = Image.fromarray(noisy_image)

            # Pass the noisy image to the view for display
            self.view_noise.noisy_image_pil = noisy_image_pil
            self.view_noise.display_image(noisy_image_pil)
     

    def apply_pixel_face(self):
        if self.cv2_img is not None:
            self.view_pixel_face = PixelFaceView(self.root, self,self.cv2_img)
            self.view_pixel_face.show_images() 
            self.view_pixel_face.window.grab_set()
            self.root.wait_window(self.view_pixel_face.window)

    def update_image(self, val=None):
        if self.view_adjust is not None:
            alpha = self.view_adjust.get_contrast() / 100  
            beta = self.view_adjust.get_brightness() - 100  
            gamma = self.view_adjust.get_gamma() / 100 

            adjusted_image = self.model.adjust_contrast_brightness(self.cv2_img.copy(), alpha, beta)
            final_image = self.model.adjust_gamma(adjusted_image, gamma)

            self.view_adjust.display_image(final_image)


    def lib_set_params(self):
        ND_POINTER_3 = np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags="C")
        if self.cuda_available:
            self.lib.run_gpu_filter.argtypes = [ND_POINTER_3, ND_POINTER_3, ct.c_size_t, ct.c_size_t]
            self.lib.run_gpu_filter.restype = None
        else:   
            self.lib.run_cpu_filter.argtypes = [ND_POINTER_3, ND_POINTER_3, ct.c_size_t, ct.c_size_t]
            self.lib.run_cpu_filter.restype = None
            
    def get_lib(self):
        lib_dir = os.path.join(os.path.dirname(__file__), "libs")
        try:
            if platform.system() == "Windows":
                lib_path = os.path.join(lib_dir, "gpu_filtering.dll" if self.cuda_available else "cpu_filtering.dll")
                self.lib = ct.windll.LoadLibrary(lib_path)
            else:  # Linux or other platforms
                if self.is_arm_linux():

                    lib_path = os.path.join(lib_dir, "libgpu_filtering_arm.so" if self.cuda_available else "libcpu_filtering_arm.so")
                else:
                    lib_path = "libcpu_filtering.so"#not get compiled gpu for x64
                self.lib = ct.CDLL(lib_path)  # Use CDLL for Linux
        except OSError as e:
            print("Error loading libraries:", e)
            return None   
        
        self.lib_set_params()
        return self.lib

    def is_arm_linux(self):
        try:
            uname_output = subprocess.check_output(['uname', '-m']).decode().strip()
            return uname_output in ['armv7l', 'aarch64']
        except subprocess.CalledProcessError as e:
            print(f"Error checking architecture: {e}")
            return False


    def apply_median_filter(self):
        if self.cv2_img is not None:
            # Load the appropriate library
            if self.get_lib() is None:
                print("Failed to load the library.")
                return

            def median_filter_operation():
                img_in = self.cv2_img.astype('float32')
                img_out = np.zeros_like(self.cv2_img, dtype=np.float32)
                try:
                    height, width, _ = img_in.shape
                    num_pixels = height * width
                    num_megapixels = num_pixels / 1_000_000  
                
                    if self.cuda_available:
                        print("Running GPU")
                        start_time = time.time() 
                        self.lib.run_gpu_filter(img_out, img_in, height, width)
                    else:
                        print("Running two CPU-Cores")
                        start_time = time.time()  
                        self.lib.run_cpu_filter(img_out, img_in, height, width)
                    
                    end_time = time.time() 
                    execution_time = end_time - start_time
                    megapixels_per_sec = num_megapixels / execution_time
                    print(f"Process Ok! Execution time: {execution_time:.4f} seconds")
                    print(f"Megapixels per second: {megapixels_per_sec:.2f} MP/s")
                
                    median_filtered_image = img_out.astype('uint8')
                    if median_filtered_image is not None:
                        # Call the UI update function from the main thread
                        self.root.after(0, lambda: FilterView(self.root, self, self.cv2_img, median_filtered_image))
                except Exception as e:
                    print("Error during median_filter_operation() execution:", e)

            # Create a new thread for the median filter operation
            thread = Thread(target=median_filter_operation)
            thread.start()

    


    def save_image(self, image):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                  filetypes=[("PNG files", "*.png"), ("All Files", "*.*")])
        if file_path:
            cv2.imwrite(file_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            messagebox.showinfo("Save Image", "Image saved successfully.")
            
    def get_system_info(self):
        cpu_info = platform.processor()
        ram_info = psutil.virtual_memory()
        ram_total_gb = ram_info.total / (1024 ** 3)
        num_cores = psutil.cpu_count(logical=True)

        gpu_info = ""
        isThereCUDA = numba.cuda.is_available()
        if isThereCUDA:
            gpu_device = numba.cuda.get_current_device()
            name = gpu_device.name
            if isinstance(name, bytes):
                name = name.decode('utf-8')

            compute_capability = '.'.join(map(str, gpu_device.compute_capability))
            gpu_info = f"Name: {name}\nCompute Capability: {compute_capability}"
        else:
            gpu_info = "No CUDA"

        system_info = (
            f"System Information:\n\n"
            f"CPU: {cpu_info}\n"
            f"RAM: {ram_total_gb:.2f} GB\n"
            f"Number of CPU Cores: {num_cores}\n\n"
            f"CUDA enabled GPU Information:\n\n{gpu_info}\n\n"
        )
        return system_info

    def show_hardware_settings(self):
        selected_option = "CPU"
        hw_window = Toplevel(self.root)
        hw_window.title("Hardware Settings")
        isThereCUDA = numba.cuda.is_available()

        def accept_settings():
            self.execution_mode = hardware_var.get()
            hw_window.destroy()

        hardware_var = StringVar(value="CPU")
        cpu_radio = tk.Radiobutton(hw_window, text="CPU Execution", variable=hardware_var, value="CPU")
        gpu_radio = tk.Radiobutton(hw_window, text="GPU Execution", variable=hardware_var, value="GPU")

        if not isThereCUDA:
            gpu_radio.config(state=DISABLED)

        cpu_radio.pack(anchor=W, padx=20, pady=5)
        gpu_radio.pack(anchor=W, padx=20, pady=5)

        accept_button = tk.Button(hw_window, text="Accept", command=accept_settings)
        accept_button.pack(pady=10)



