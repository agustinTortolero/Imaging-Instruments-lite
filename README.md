# Imaging-Toolbox-lite
Image Processing Application for Windows
Description
The provided code implements an MVC (Model-View-Controller) architecture for an image processing application using the Tkinter library for the GUI, OpenCV for image processing, and Matplotlib for displaying histograms. The application allows users to load images, apply Sobel edge detection, and perform histogram equalization on color images using the HSI (Hue, Saturation, Intensity) color space.

Key Components
Model (ImageModel.py)
The ImageModel class provides methods for opening images and applying Sobel edge detection and histogram equalization.

View (ImageViewer.py)
The ImageViewer class creates the GUI elements for displaying images and buttons for interacting with the application.

Controller (ImageController.py)
The ImageController class handles user interactions and coordinates communication between the model and view. It contains methods for loading images, applying Sobel edge detection, displaying images, and showing histogram equalization windows.

Main Application (main.py)
The main.py script initializes the Tkinter application, creates the controller, and sets up the menu bar for system information and saving images.

Functionality
Users can load images in PNG, JPG, or BMP format using a file dialog.
The application displays loaded images and applies Sobel edge detection to highlight edges.
Users can view the original and Sobel-processed images along with their histograms.
Histogram equalization can be performed on color images using the HSI color space. The equalized image and histograms are displayed in a separate window.
The application provides options to save the equalized image and quit the histogram equalization window.
Overall, this MVC image processing application offers an intuitive interface for loading, processing, and analyzing images, making it useful for both beginner and advanced users in various fields, including computer vision, image processing, and digital photography.
