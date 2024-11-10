import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk
import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

from .base_view import BaseView

class ZoomWindow(tk.Toplevel, BaseView):
    def __init__(self, master, original_image):
        super().__init__(master)
        self.title("Inspect")
        self.master = master
        self.original_image = original_image

        self.display_image = np.zeros_like(self.original_image)

        self.zoom_factor = 2.0
        self.max_zoom_factor = 10.0
        self.min_zoom_factor = 0.1
        self.mouse_position = None

        self.fixed_zoom_width = 100
        self.fixed_zoom_height = 100

        self.original_fig = plt.figure(figsize=(10, 5))
        self.ax1 = self.original_fig.add_subplot(121)
        self.ax2 = self.original_fig.add_subplot(122)
        self.original_canvas = self.create_canvas(self.original_fig)

        self.frame = tk.Frame(self)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.original_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.r_frame = tk.Frame(self.frame, bg="red", width=150, height=150)
        self.g_frame = tk.Frame(self.frame, bg="green", width=150, height=150)
        self.b_frame = tk.Frame(self.frame, bg="blue", width=150, height=150)

        self.r_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True, anchor=tk.CENTER)
        self.g_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True, anchor=tk.CENTER)
        self.b_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True, anchor=tk.CENTER)

        self.r_entries = self.create_entry_grid(self.r_frame, "lightcoral")
        self.g_entries = self.create_entry_grid(self.g_frame, "lightgreen")
        self.b_entries = self.create_entry_grid(self.b_frame, "lightblue")

        self.coord_text = None  # Add a variable to keep track of the coordinate text object

        self.update_pixel_matrix(0, 0)
        self.show_images()

        self.create_context_menu()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Bind right-click event to show context menu
        self.original_canvas.get_tk_widget().bind("<Button-3>", self.show_context_menu)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Save Image", command=self.save_region_of_interest)

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def create_canvas(self, fig):
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas_widget.bind("<MouseWheel>", self.on_mouse_wheel)
        canvas_widget.bind("<Motion>", self.on_mouse_move)
        return canvas

    def show_images(self):
        self.ax1.clear()
        self.ax1.imshow(self.original_image)
        self.ax1.set_title('Original')
        self.ax1.axis('off')

        self.ax2.clear()
        self.ax2.imshow(self.original_image)
        self.ax2.set_title('Region of Interest')
        self.ax2.axis('off')

        self.original_canvas.draw()

    def update_zoomed_image(self):
        if self.mouse_position is None:
            return

        x, y = self.mouse_position
        zoomed_width = int(self.fixed_zoom_width * self.zoom_factor)
        zoomed_height = int(self.fixed_zoom_height * self.zoom_factor)

        zoomed_x1 = max(0, int(x - zoomed_width / 2))
        zoomed_x2 = min(self.original_image.shape[1], int(x + zoomed_width / 2))
        zoomed_y1 = max(0, int(y - zoomed_height / 2))
        zoomed_y2 = min(self.original_image.shape[0], int(y + zoomed_height / 2))

        self.display_image = self.original_image.copy()
        cv2.rectangle(self.display_image, (zoomed_x1, zoomed_y1), (zoomed_x2, zoomed_y2), (42, 42, 165), 2)

        zoomed_image = self.original_image[zoomed_y1:zoomed_y2, zoomed_x1:zoomed_x2]

        if zoomed_image.size == 0:
            return

        self.ax1.clear()
        self.ax1.imshow(self.display_image)
        self.ax1.set_title('Original')

        self.ax2.clear()
        self.ax2.imshow(zoomed_image)
        self.ax2.set_title('Region of Interest')

        self.update_pixel_matrix(x, y)

        if self.coord_text:
            self.coord_text.remove()  # Remove the previous coordinate text

        # Display the current coordinates on the original image
        self.coord_text = self.ax1.text(
            0.02, 0.98,  # Position in normalized figure coordinates
            f'X: {int(x)}, Y: {int(y)}',  # Use int() to convert to integers
            transform=self.ax1.transAxes,
            fontsize=12,
            verticalalignment='top',
            color='white',
            bbox=dict(facecolor='black', alpha=0.7, edgecolor='none')
        )

        self.original_canvas.draw()

    def create_entry_grid(self, frame, center_color):
        entries = []
        for i in range(5):
            row_entries = []
            for j in range(5):
                entry = tk.Entry(frame, font=("Courier", 12), width=3, justify='center')
                if i == 2 and j == 2:
                    entry.config(bg=center_color)
                entry.grid(row=i, column=j, padx=1, pady=1, sticky='nsew')
                row_entries.append(entry)
            entries.append(row_entries)

        for i in range(5):
            frame.grid_rowconfigure(i, weight=1)
            frame.grid_columnconfigure(i, weight=1)

        return entries

    def update_pixel_matrix(self, x, y):
        x = int(x)
        y = int(y)
        half_size = 2
        matrices = {}
        for channel in range(3):
            matrix = self.original_image[
                max(0, y - half_size):min(y + half_size + 1, self.original_image.shape[0]),
                max(0, x - half_size):min(x + half_size + 1, self.original_image.shape[1]),
                channel
            ]

            if matrix.shape[0] < 5 or matrix.shape[1] < 5:
                padded_matrix = np.zeros((5, 5), dtype=matrix.dtype)
                padded_matrix[:matrix.shape[0], :matrix.shape[1]] = matrix
                matrix = padded_matrix

            matrices[channel] = matrix

        for channel, matrix in matrices.items():
            for i, row in enumerate(matrix):
                for j, value in enumerate(row):
                    if channel == 0:
                        self.r_entries[i][j].delete(0, tk.END)
                        self.r_entries[i][j].insert(0, str(value))
                    elif channel == 1:
                        self.g_entries[i][j].delete(0, tk.END)
                        self.g_entries[i][j].insert(0, str(value))
                    else:
                        self.b_entries[i][j].delete(0, tk.END)
                        self.b_entries[i][j].insert(0, str(value))

    def on_mouse_move(self, event):
        canvas_widget = self.original_canvas.get_tk_widget()
        widget_width, widget_height = canvas_widget.winfo_width(), canvas_widget.winfo_height()

        bbox = self.ax1.get_window_extent().transformed(self.original_fig.dpi_scale_trans.inverted())
        ax1_width, ax1_height = bbox.width * self.original_fig.dpi, bbox.height * self.original_fig.dpi
        ax1_left, ax1_bottom = bbox.x0 * self.original_fig.dpi, bbox.y0 * self.original_fig.dpi

        if ax1_left <= event.x <= ax1_left + ax1_width and ax1_bottom <= event.y <= ax1_bottom + ax1_height:
            x_norm = (event.x - ax1_left) / ax1_width
            y_norm = (event.y - ax1_bottom) / ax1_height

            x_img = x_norm * self.original_image.shape[1]
            y_img = y_norm * self.original_image.shape[0]

            self.mouse_position = (x_img, y_img)

            self.update_zoomed_image()
            canvas_widget.config(cursor="crosshair")
        else:
            self.mouse_position = None
            canvas_widget.config(cursor="")
            # Clear the coordinates text on the original image
            if self.coord_text:
                self.coord_text.remove()
                self.coord_text = None
            self.original_canvas.draw()

    def on_mouse_wheel(self, event):
        if event.delta < 0:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor /= 1.1

        self.zoom_factor = max(self.min_zoom_factor, min(self.zoom_factor, self.max_zoom_factor))
        self.update_zoomed_image()

    def save_region_of_interest(self):
        if self.mouse_position is None:
            messagebox.showwarning("Save Image", "Please select a region to save.")
            return

        x, y = self.mouse_position
        zoomed_width = int(self.fixed_zoom_width * self.zoom_factor)
        zoomed_height = int(self.fixed_zoom_height * self.zoom_factor)

        zoomed_x1 = max(0, int(x - zoomed_width / 2))
        zoomed_x2 = min(self.original_image.shape[1], int(x + zoomed_width / 2))
        zoomed_y1 = max(0, int(y - zoomed_height / 2))
        zoomed_y2 = min(self.original_image.shape[0], int(y + zoomed_height / 2))

        roi = self.original_image[zoomed_y1:zoomed_y2, zoomed_x1:zoomed_x2]

        if roi.size == 0:
            messagebox.showerror("Save Image", "No region selected.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )

        if save_path:
            Image.fromarray(roi).save(save_path)
            messagebox.showinfo("Save Image", f"Image saved successfully to {save_path}")

    def on_close(self):
        self.destroy()# for closing tk.Toplevel
