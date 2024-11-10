import os
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk
import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

from .base_view import BaseView
from models import ImageModel

class PixelFaceView(BaseView):
    def __init__(self, root, controller, original_image_cv):
        super().__init__(root, controller)
        self.controller = controller
        self.model = ImageModel()
        self.image_cv = original_image_cv  # Store the image as numpy array
        self.image_pil = Image.fromarray(self.image_cv)  # Convert to PIL format
        self.title = "PixelFaces"

    def show_images(self):
        self.window = tk.Toplevel(self.root)
        self.window.title("PixelFace")

        # Create menu bar
        menubar = self.create_menu_bar()
        self.window.config(menu=menubar)

        # Left Frame for controls
        left_frame = tk.Frame(self.window)
        left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="n")

        # Pixelation Level Scale
        label_pixelation = tk.Label(left_frame, text="Pixelation Level")
        label_pixelation.grid(row=0, column=0, padx=5, pady=5)
        self.scale_pixelation = tk.Scale(left_frame, from_=1, to=30, orient=tk.HORIZONTAL, command=self.update_image)
        self.scale_pixelation.set(1)  # Default value of 10
        self.scale_pixelation.grid(row=0, column=1, padx=5, pady=5)

        # Right Frame for image display
        right_frame = tk.Frame(self.window)
        right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="n")

        # Example of displaying image
        self.label_image = tk.Label(right_frame)
        self.label_image.pack()

        # Display the original image
        self.display_image(self.image_cv)

        # Bind right-click for context menu
        self.label_image.bind("<Button-3>", self.on_right_click)

    def on_right_click(self, event):
        # Show context menu
        self.show_context_menu(event, self.image_pil)

    def update_image(self, event=None):
        # Get pixelation level from scale
        pixelation_level = self.scale_pixelation.get()

        # Apply pixelation on faces
        pixelated_image_cv = self.model.pixelate_faces(self.image_cv.copy(), pixelation_level)

        # Convert to PIL image for context menu
        pixelated_image_pil = Image.fromarray(pixelated_image_cv)

        # Display updated image
        self.display_image(pixelated_image_cv)

        # Update the image_pil attribute to the newly processed image
        self.image_pil = pixelated_image_pil

    def display_image(self, image_cv):
        # Convert OpenCV image to PIL Image
        image_pil = Image.fromarray(image_cv)

        # Resize the image to half its size while maintaining aspect ratio
        max_width, max_height = image_pil.size[0] // 2, image_pil.size[1] // 2
        image_pil_resized = self.resize_with_aspect_ratio(image_pil, max_width, max_height)

        # Convert the resized PIL Image to PhotoImage
        photo_image = ImageTk.PhotoImage(image_pil_resized)

        # Update label with the new image
        self.label_image.config(image=photo_image)
        self.label_image.image = photo_image

    def save_image_pixelate(self):
        if self.image_pil is None:
            messagebox.showerror("Save Image", "Image is not available.")
            return

        # Save the processed image using the BaseView's method
        self.save_image(self.image_pil, "Pixelated Image")
