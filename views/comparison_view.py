import os
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Menu
from PIL import Image, ImageTk
import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

from .base_view import BaseView


class ComparisonView(BaseView):
    def __init__(self, root, controller, original_image_cv, processed_image_cv, title):
        super().__init__(root, controller)
        self.original_image_cv = original_image_cv
        self.processed_image_cv = processed_image_cv
        self.title = title
        self.window = None  # Store the Toplevel window
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.show_images()

    def show_images(self):
        original_image_pil, processed_image_pil = self.convert_images()
        original_image_resized, processed_image_resized_display = self.resize_images(original_image_pil, processed_image_pil)
        original_photo, processed_photo = self.convert_to_photoimage(original_image_resized, processed_image_resized_display)
        self.create_window()
        self.display_images(original_photo, processed_photo, processed_image_pil)
        self.root.wait_window(self.window)

    def convert_images(self):
        """Convert OpenCV images to PIL images."""
        original_image_pil = Image.fromarray(self.original_image_cv)
        processed_image_pil = Image.fromarray(self.processed_image_cv)
        return original_image_pil, processed_image_pil

    def resize_images(self, original_image_pil, processed_image_pil):
        """Resize images while preserving aspect ratio."""
        max_width = 700
        max_height = 700
        original_image_resized = self.resize_with_aspect_ratio(original_image_pil, max_width, max_height)
        processed_image_resized_display = self.resize_with_aspect_ratio(processed_image_pil, max_width, max_height)
        return original_image_resized, processed_image_resized_display

    def convert_to_photoimage(self, original_image_resized, processed_image_resized_display):
        """Convert PIL images to PhotoImage objects."""
        original_photo = ImageTk.PhotoImage(original_image_resized)
        processed_photo = ImageTk.PhotoImage(processed_image_resized_display)
        return original_photo, processed_photo

    def create_window(self):
        """Create and configure the Toplevel window."""
        if self.window is None or not self.window.winfo_exists():
            self.window = tk.Toplevel(self.root)
            self.window.title(self.title)
            self.window.protocol("WM_DELETE_WINDOW", self.on_close)
            self.create_menu_bar()  # Call the menu bar creation method
            # Make the window modal
            self.window.transient(self.root)  # Make the window appear above the main window
            self.window.grab_set()  # Capture all events and direct them to this window

            self.create_menu_bar()
        else:
            # Clear the window widgets but keep the menu
            for widget in self.window.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.destroy()


    def display_images(self, original_photo, processed_photo, processed_image_pil):
        """Display the images in the Toplevel window."""
        # Display the original image
        original_label = tk.Label(self.window, text="Original Image")
        original_label.pack()
        original_image_label = tk.Label(self.window, image=original_photo)
        original_image_label.image = original_photo
        original_image_label.pack()

        # Display the processed image
        processed_label = tk.Label(self.window, text=self.title)
        processed_label.pack()
        processed_image_label = tk.Label(self.window, image=processed_photo)
        processed_image_label.image = processed_photo
        processed_image_label.pack()

        # Add context menu to the processed image
        processed_image_label.bind("<Button-3>", lambda event: self.show_context_menu(event, self.processed_image_cv))