import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from .base_view import BaseView
import numpy as np


class NoiseGeneratorView(BaseView):
    def __init__(self, root, controller, original_image_cv):
        super().__init__(root, controller)
        self.original_image_cv = original_image_cv
        self.noisy_image_pil = None
        self.image_pil = None  # for displaying
        self.create_window()
        self.create_context_menu()
        self.title = "Inject Noise"

    def create_window(self):
        self.window = tk.Toplevel(self.root)
        self.window.title("Image Noise Generator")
        self.create_menu_bar()

        left_frame = tk.Frame(self.window)
        left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="n")

        tk.Label(left_frame, text="Noise Type").grid(row=0, column=0, padx=5, pady=5)
        self.combo_noise_type = tk.StringVar(value="Salt and Pepper")
        tk.OptionMenu(left_frame, self.combo_noise_type, "Salt and Pepper", "Gaussian").grid(row=0, column=1, padx=5, pady=5)

        tk.Label(left_frame, text="Noise Density (%)").grid(row=1, column=0, padx=5, pady=5)
        self.scale_noise_density = tk.Scale(left_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.scale_noise_density.set(50)
        self.scale_noise_density.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(left_frame, text="Run", command=self.apply_noise).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="we")

        right_frame = tk.Frame(self.window)
        right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="n")

        self.label_image = tk.Label(right_frame)
        self.label_image.pack()

        self.label_image.bind("<Button-3>", self.show_context_menu)

        self.display_image(self.original_image_cv)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="Save Image", command=lambda: self.save_image(self.noisy_image_pil, self.title))

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def apply_noise(self):
        noise_type = self.combo_noise_type.get()
        noise_density = self.scale_noise_density.get()

        # Apply noise to the original image
        self.controller.apply_noise(self.original_image_cv, noise_type, noise_density)

        # Update the displayed image with the processed one
        self.display_image(self.noisy_image_pil)

        # Clear the previously processed image
        self.processed_image_cv = None

    def display_image(self, image_pil):
        # Assign the processed image to self.noisy_image_pil for saving
        self.noisy_image_pil = image_pil

        # Resize the image and update the display
        image_pil_resized = self.resize_with_aspect_ratio(image_pil, image_pil.size[0] // 2, image_pil.size[1] // 2)
        photo_image = ImageTk.PhotoImage(image_pil_resized)
        self.label_image.config(image=photo_image)
        self.label_image.image = photo_image