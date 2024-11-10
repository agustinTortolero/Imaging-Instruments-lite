import os
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk
import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

from .base_view import BaseView

class HistogramView(BaseView):
    def __init__(self, root, controller, original_image, original_hist, processed_image_cv, equalized_hist):
        super().__init__(root, controller)
        self.original_image = original_image
        self.original_hist = original_hist
        self.processed_image_cv = processed_image_cv
        self.equalized_hist = equalized_hist

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.window = None  # Store the Toplevel window
        self.title = "Contrast Enhancement"
        self.show_histogram_equalization_window()

    def show_histogram_equalization_window(self):
        self.setup_window()
        self.create_menu_bar()
        self.create_histogram_plots()
        self.window.grab_set()

    def setup_window(self):
        self.window = tk.Toplevel(self.root)
        self.window.title(self.title)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.geometry(f"{self.screen_width}x{self.screen_height}")

    def create_histogram_plots(self):
        # Create Matplotlib figure and axis
        fig = plt.figure(figsize=(10, 5))
        ax1 = fig.add_subplot(221)
        ax2 = fig.add_subplot(222)
        ax3 = fig.add_subplot(223)
        ax4 = fig.add_subplot(224)

        # Display original image and histogram
        self.plot_original_image(ax1)
        self.plot_histogram(ax2, self.original_hist, 'Original Histogram')

        # Display equalized image and histogram
        self.plot_equalized_image(ax3)
        self.plot_histogram(ax4, self.equalized_hist, 'Enhanced Histogram')

        plt.tight_layout()

        # Convert the matplotlib plot to a Tkinter-compatible format
        plt_canvas = FigureCanvasTkAgg(fig, master=self.window)
        plt_canvas.draw()
        plt_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Bind right-click event to show context menu
        plt_canvas.get_tk_widget().bind("<Button-3>", lambda event: self.show_context_menu(event, self.processed_image_cv))

    def plot_original_image(self, ax):
        ax.imshow(self.original_image)
        ax.set_title('Original Image')
        ax.axis('off')

    def plot_equalized_image(self, ax):
        ax.imshow(self.processed_image_cv)
        self.processed_image_cv = cv2.cvtColor(self.processed_image_cv, cv2.COLOR_BGR2RGB)
        ax.set_title('Equalized Image')
        ax.axis('off')

    def plot_histogram(self, ax, hist, title):
        colors = ('b', 'g', 'r')
        for i in range(3):
            ax.plot(hist[i], color=colors[i])
        ax.set_title(title)
        ax.set_xlim([0, 256])
