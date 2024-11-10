import tkinter as tk
import os
from tkinter import filedialog, messagebox, Toplevel,Menu
from PIL import Image, ImageTk
import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

class BaseView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.window = None
        self.label_image = None
        self.script_dir = os.path.dirname(os.path.abspath(__file__))


    def create_button(self, parent, text, command, state=tk.NORMAL):
        button = tk.Button(parent, text=text, command=command, state=state)
        button.pack(side="left", padx=10, pady=10)
        return button

    def create_option_menu(self, parent, variable, options):
        option_menu = tk.OptionMenu(parent, variable, *options)
        option_menu.pack(side="left", padx=10, pady=10)
        option_menu.config(state=tk.DISABLED)  # Initially disabled
        return option_menu

    def enable_buttons(self):
        raise NotImplementedError("This method should be overridden in the subclass")

    def update_loaded_image_label(self, file_path):
        loaded_image_label = tk.Label(self.root, text="Loaded Image Path: " + file_path)
        loaded_image_label.pack()

    def resize_with_aspect_ratio(self, image, max_width, max_height):
        """Resize the image while preserving aspect ratio."""
        width, height = image.size
        aspect_ratio = width / height

        if aspect_ratio > 1:
            new_width = min(width, max_width)
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = min(height, max_height)
            new_width = int(new_height * aspect_ratio)

        return image.resize((new_width, new_height))

    def save_image(self, image, title):
        filetypes = [
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg;*.jpeg"),
            ("BMP files", "*.bmp"),
            ("TIFF files", "*.tiff;*.tif")
        ]
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=filetypes)
        if file_path:
            if isinstance(image, Image.Image):
            # If the image is a PIL image
                pil_size = image.size  # (width, height)
                print(f"PIL image size: {pil_size}")
            
            # Save the PIL image directly
                image.save(file_path)
                messagebox.showinfo("Save Image", f"Image saved as {file_path} (PIL format).")
        
            elif isinstance(image, np.ndarray):
            # If the image is an OpenCV image
                cv_size = image.shape  # (height, width, channels)
                print(f"OpenCV image size: {cv_size}")
            
            # Convert to BGR if the image is in RGB
                if len(cv_size) == 3 and cv_size[2] == 3:  # Checking if it's a color image
                    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                else:
                    image_bgr = image
            
            # Save the OpenCV image using cv2.imwrite
                success = cv2.imwrite(file_path, image_bgr)
                if success:
                    messagebox.showinfo("Save Image", f"Image saved as {file_path} (OpenCV format).")
                else:
                    messagebox.showerror("Save Image", "Failed to save the image.")
        
            else:
                raise ValueError("Unsupported image type. The image must be a PIL image or an OpenCV image.")



    def show_about_info(self):
        descriptions_file_paths = {
            "Inject Noise": os.path.join(self.script_dir, "..", "assets", "description_noiseGen.txt"),
            "Contrast Enhancement":os.path.join(self.script_dir, "..", "assets", "description_histeq.txt"),
            "Adjust":os.path.join(self.script_dir, "..", "assets", "description_adjust.txt"),
            "PixelFaces":os.path.join(self.script_dir, "..", "assets", "description_pixelFace.txt"),
            
            "Edges Detection": os.path.join(self.script_dir, "..", "assets", "description_edges.txt"),
            "Impulse Filter": os.path.join(self.script_dir, "..", "assets", "description_impulseFilter.txt"),
            "Gaussian Filter": os.path.join(self.script_dir, "..", "assets", "description_gaussianFilter.txt")
            
        }

    # Determine the correct description file based on the title
        description_file_path = descriptions_file_paths.get(self.title)
    
        if not description_file_path:
            description = "No additional information available."
        else:
        # Read the description from the text file
            try:
                with open(description_file_path, "r") as file:
                    description = file.read()
            except FileNotFoundError:
                description = "Description file not found. Please ensure the file exists."

    # Create the about window
        about_window = tk.Toplevel(self.window)  # Use self.window as parent
        about_window.title("About Function")
        about_window.geometry("800x600")
        about_window.resizable(False, False)  # Lock the window size
        about_window.protocol("WM_DELETE_WINDOW", about_window.destroy)  # Close dialog on 'x' button

    # Make the about window modal
        about_window.transient(self.window)  # Make the about window a child of self.window
        about_window.grab_set()  # Grab all events for the about window

    # Create a Text widget to display the description
        text_widget = tk.Text(about_window, wrap=tk.WORD, font=("Verdana", 12), padx=10, pady=10)
        text_widget.tag_configure("spacing", spacing1=15, spacing2=10, spacing3=10)

        text_widget.insert(tk.END, description, "spacing")
        text_widget.config(state=tk.DISABLED)  # Make the text widget read-only
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


    def show_context_menu(self, event, processed_image_pil):
        context_menu = Menu(self.window, tearoff=0)
        context_menu.add_command(label="Save Image", command=lambda: self.save_image(processed_image_pil, self.title))
        context_menu.post(event.x_root, event.y_root)

    def on_close(self):
        if self.window:
            self.window.destroy()
            self.window = None  # Reset window reference


    def create_menu_bar(self):
        """Create and configure the menu bar."""
        if not self.window:
            raise ValueError("Window is not created yet.")
        
        menu_bar = tk.Menu(self.window)
        self.window.config(menu=menu_bar)

        # Create 'File' menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label=f"Save image", command=self.save_current_image)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.on_close)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Create 'Info' menu
        menu_bar.add_command(label="Info", command=self.show_about_info)
        
    def save_current_image(self):
        if self.noisy_image_pil is not None:
            self.save_image(self.noisy_image_pil, self.title)
        else:
            messagebox.showwarning("Save Image", "No image to save.")