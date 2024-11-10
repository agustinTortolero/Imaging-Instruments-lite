import os
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk
import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

from .base_view import BaseView

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import numpy as np
import cv2

class ImageAdjustmentView(BaseView):
    def __init__(self, root, controller, original_image_cv):
        super().__init__(root, controller)
        self.image_cv = original_image_cv
        self.image_pil = Image.fromarray(self.image_cv)
        self.window = None
        self.context_menu = None  # Initialize the context menu attribute
        self.create_window()  # Initialize the window and menu
        self.title = "Adjust"

    def create_window(self):
        if not hasattr(self, 'window') or self.window is None or not self.window.winfo_exists():
            self.window = tk.Toplevel(self.root)
            self.window.title("Image Adjustments")

            # Create the menu bar
            self.create_menu_bar()

            # Left Frame for controls
            left_frame = tk.Frame(self.window)
            left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="n")

            # Contrast Scale
            tk.Label(left_frame, text="Contrast").grid(row=0, column=0, padx=5, pady=5)
            self.scale_contrast = tk.Scale(left_frame, from_=0, to=300, orient=tk.HORIZONTAL, command=self.update_image)
            self.scale_contrast.set(100)
            self.scale_contrast.grid(row=0, column=1, padx=5, pady=5)

            # Brightness Scale
            tk.Label(left_frame, text="Brightness").grid(row=1, column=0, padx=5, pady=5)
            self.scale_brightness = tk.Scale(left_frame, from_=0, to=200, orient=tk.HORIZONTAL, command=self.update_image)
            self.scale_brightness.set(100)
            self.scale_brightness.grid(row=1, column=1, padx=5, pady=5)

            # Gamma Scale
            tk.Label(left_frame, text="Gamma").grid(row=2, column=0, padx=5, pady=5)
            self.scale_gamma = tk.Scale(left_frame, from_=10, to=200, orient=tk.HORIZONTAL, command=self.update_image)
            self.scale_gamma.set(100)
            self.scale_gamma.grid(row=2, column=1, padx=5, pady=5)

            # Right Frame for image display
            right_frame = tk.Frame(self.window)
            right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="n")

            # Image display label
            self.label_image = tk.Label(right_frame)
            self.label_image.pack()

            # Create the context menu
            self.create_context_menu()

            # Bind right-click to show context menu
            self.label_image.bind("<Button-3>", self.show_context_menu_handler)

            # Schedule initial image display
            self.window.after(100, self.display_image, self.image_cv)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="Save Image", command=self.save_image_handler)

    def show_context_menu_handler(self, event):
        self.show_context_menu(event)

    def show_context_menu(self, event):
        # Show the context menu at the position of the cursor
        self.context_menu.post(event.x_root, event.y_root)

    def save_image_handler(self):
        adjusted_image = self.apply_adjustments(self.image_cv)
        image_pil = Image.fromarray(adjusted_image)
        self.save_image(image_pil, "Save Adjusted Image")

    def display_image(self, image_cv):
        image_pil = Image.fromarray(image_cv)

        # Resize the image to half its size while maintaining aspect ratio
        max_width, max_height = image_pil.size[0] // 2, image_pil.size[1] // 2
        image_pil_resized = self.resize_with_aspect_ratio(image_pil, max_width, max_height)

        # Convert the resized PIL Image to PhotoImage
        photo_image = ImageTk.PhotoImage(image_pil_resized)

        # Update label with the new image
        self.label_image.config(image=photo_image)
        self.label_image.image = photo_image

        #TODO: send to controller
    def apply_adjustments(self, image): 
        contrast = self.get_contrast() / 100.0
        brightness = self.get_brightness() - 100
        gamma = self.get_gamma() / 100.0

        adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        adjusted = cv2.LUT(adjusted, table)
        return adjusted

    def get_contrast(self):
        return self.scale_contrast.get()

    def get_brightness(self):
        return self.scale_brightness.get()

    def get_gamma(self):
        return self.scale_gamma.get()

    def update_image(self, _):
        adjusted_image = self.apply_adjustments(self.image_cv)
        self.display_image(adjusted_image)
