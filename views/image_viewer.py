import os
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Menu, PhotoImage
from PIL import Image, ImageTk
import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from tkinter import font as tkfont



from .base_view import BaseView

class ImageViewer(BaseView):
    def __init__(self, root, controller):
        super().__init__(root, controller)
        self.create_menu()
        self.create_image_placeholder(self.root)

        self.set_initial_window_size()
        self.center_window()
        self.lock_window_size()
        
        self.image_loaded = False  # Initialize image_loaded as False
        
        # Initialize context menu
        self.create_context_menu()

    def create_image_placeholder(self, parent):
        # Get the background color of the parent window
        bg_color = parent.cget('background')

        # Create the image label with the standard window background color
        self.label_image = tk.Label(parent, width=800, height=450, bg=bg_color)
        self.label_image.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a label in the middle of the placeholder
        self.placeholder_label = tk.Label(parent, text="Left click here, then right-click.", bg="gray", fg="white", font=("Consolas", 15))
        self.placeholder_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Bind click event to the placeholder label
        self.placeholder_label.bind("<Button-1>", self.on_label_click)

        # Bind right-click to the image label to show context menu
        self.label_image.bind("<Button-3>", self.show_context_menu)

    def create_context_menu(self):
        # Create context menu with required options
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Inspect", command=self.controller.inspect)
        self.context_menu.add_command(label="Inject Noise", command=self.controller.apply_noise)
        self.context_menu.add_command(label="Edges Detection", command=self.controller.apply_sobel)
        self.context_menu.add_command(label="Contrast Enhancement", command=self.controller.apply_histogram_equalization)
        self.context_menu.add_command(label="Adjust", command=self.controller.apply_adjust)
        self.context_menu.add_command(label="Impulse Filter", command=self.controller.apply_median_filter)
        self.context_menu.add_command(label="Gaussian Filter", command=self.controller.apply_gaussian_blur)
        self.context_menu.add_command(label="PixelFaces", command=self.controller.apply_pixel_face)

        # Disable context menu initially
        self.update_context_menu_state()

    def show_context_menu(self, event):
        if self.image_loaded:  # Show context menu only if an image is loaded
            self.context_menu.post(event.x_root, event.y_root)

    def on_label_click(self, event):
        self.controller.load_image()

    def display_image(self, image):
        pil_image = Image.fromarray(image)

        # Resize the image to fit the placeholder while maintaining aspect ratio
        max_width, max_height = self.label_image.winfo_width(), self.label_image.winfo_height()
        pil_image_resized = self.resize_with_aspect_ratio(pil_image, max_width, max_height)

        # Convert the resized PIL image to a PhotoImage
        tk_image = ImageTk.PhotoImage(image=pil_image_resized)

        # Display the image in the Tkinter label
        self.label_image.config(image=tk_image)
        self.label_image.image = tk_image

        # Hide the placeholder label
        self.placeholder_label.place_forget()

        # Update the image loaded flag and context menu state
        self.image_loaded = True
        self.update_context_menu_state()

    def update_context_menu_state(self):
        # Enable or disable the context menu items based on whether an image is loaded
        state = tk.NORMAL if self.image_loaded else tk.DISABLED
        for item in self.context_menu.winfo_children():
            item.config(state=state)

    def set_initial_window_size(self):
        # Set an initial size for the window
        self.root.geometry("800x450")

    def center_window(self):
        # Update the root window dimensions if needed
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def lock_window_size(self):
        # Prevent the window from being resized
        self.root.resizable(False, False)

    def create_menu(self):
        menubar = Menu(self.root)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load Image", command=self.controller.load_image)
        file_menu.add_command(label="Quit", command=self.root.quit)

        about_menu = Menu(menubar, tearoff=0)
        about_menu.add_command(label="About Imaging Instruments lite", command=self.show_about_info)
        about_menu.add_command(label="System Info", command=self.show_system_info)

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="About", menu=about_menu)

        self.root.config(menu=menubar)

    def show_system_info(self):
        system_info = self.controller.get_system_info()
        messagebox.showinfo("System Info", system_info)
        
    def show_about_info(self):
        about_window = Toplevel(self.root)
        about_window.title("About Imaging Instruments lite")

    # Set the icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon_camera4.png')

        try:
        # Load the icon image
            icon_image = PhotoImage(file=icon_path)
            about_window.iconphoto(True, icon_image)
        except Exception as e:
            print(f"Error setting icon: {e}")

    # Set the size of the window
        width = 850
        height = 470
        about_window.geometry(f"{width}x{height}")

    # Lock the window size
        about_window.resizable(False, False)

    # Create a Text widget for rich text
        text_widget = tk.Text(about_window, wrap=tk.WORD, font=("Verdana", 12), height=19)
        text_widget.pack( padx=10, pady=(10, 1))  # Add padding to the bottom

    # Configure tags for different styles
        text_widget.tag_configure("title", font=tkfont.Font(family="Verdana", size=30, weight="bold"), foreground="blue")
        text_widget.tag_configure("version_info", font=tkfont.Font(family="Verdana", size=14))
        text_widget.tag_configure("description", font=tkfont.Font(family="Verdana", size=12))
        text_widget.tag_configure("author", font=tkfont.Font(family="Verdana", size=12))

    # Insert text with tags
        text_widget.insert(tk.END, "Imaging Instruments lite\n", "title")
        text_widget.insert(tk.END, "Version 1    MIT License\n19/08/2024\n\n", "version_info")
        description = (
            "Imaging Instruments lite is a comprehensive image processing application developed\n"
            "following the Model-View-Controller (MVC) design pattern, utilizing Python, Tkinter, and OpenCV.\n"
            "It provides users with image manipulation capabilities, leveraging multi-threading\n"
            "with OpenMP and GPU acceleration using CUDA-C.\n\n"
        )
        text_widget.insert(tk.END, description, "description")

        author_info = (
            "\nFueled by yerba mate and a passion for coding. Created by Agustin Tortolero.\n\n"
            "Contact: agustin.tortolero@proton.me\n"
            "Source code: https://github.com/agustinTortolero/Imaging-Instruments-lite"
        )
        text_widget.insert(tk.END, author_info, "author")

    # Disable editing
        text_widget.config(state=tk.DISABLED)

    # Add logos as images
        logos_frame = tk.Frame(about_window)
        logos_frame.pack(pady=10)

    # Use a grid layout for centering the logos
        logos_frame.grid_columnconfigure(0, weight=1)
        logos_frame.grid_columnconfigure(1, weight=1)
        logos_frame.grid_columnconfigure(2, weight=1)
        logos_frame.grid_columnconfigure(3, weight=1)
        logos_frame.grid_columnconfigure(4, weight=1)

        self.create_resized_logo_label(logos_frame, "Python_logo.png", 80, 0)
        self.create_resized_logo_label(logos_frame, "Cpp_logo.png", 80, 1)
        self.create_resized_logo_label(logos_frame, "OpenMP_logo.png", 100, 2)  # Centered logo
        self.create_resized_logo_label(logos_frame, "Nvidia_logo.png", 80, 3)
        self.create_resized_logo_label(logos_frame, "OpenCV_logo.png", 80, 4)

    # Make the window modal
        about_window.transient(self.root)
        about_window.grab_set()
        self.root.wait_window(about_window)

    def create_resized_logo_label(self, frame, image_name, target_size, column):
        image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', image_name)
        print(f"Attempting to load image from: {image_path}")

        try:
        # Open the image
            original_image = Image.open(image_path)

        # Calculate the new size while maintaining the aspect ratio
            original_width, original_height = original_image.size
            ratio = min(target_size / original_width, target_size / original_height)
            new_size = (int(original_width * ratio), int(original_height * ratio))

        # Resize the image to the new size
            resized_image = original_image.resize(new_size, Image.Resampling.LANCZOS)
            tk_resized_image = ImageTk.PhotoImage(resized_image)

        # Create a label and place it in the grid
            logo_label = tk.Label(frame, image=tk_resized_image)
            logo_label.image = tk_resized_image  # Keep a reference to prevent garbage collection
            logo_label.grid(row=0, column=column, padx=10)  # Place logos in grid columns

            print("Image loaded successfully.")

        except Exception as e:
            print(f"Error loading image '{image_name}': {e}")


    def resize_with_aspect_ratio(self, pil_image, max_width, max_height):
        # Resize image while maintaining the aspect ratio
        original_width, original_height = pil_image.size
        ratio = min(max_width / original_width, max_height / original_height)
        new_size = (int(original_width * ratio), int(original_height * ratio))
        return pil_image.resize(new_size, Image.Resampling.LANCZOS)

    def destroy(self):
        # Unload resources
        self.root.quit()
        self.root.destroy()
