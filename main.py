import tkinter as tk
from controller import ImageController
from views import SplashScreen, ImageViewer

def main():
    root = tk.Tk()

    root.withdraw()  # Hide the main window while splash screen is showing

    splash = SplashScreen(root)
    controller = ImageController(root)
    #viewer = ImageViewer(root, controller)

    root.title("Imaging Instruments lite")
    root.mainloop()

if __name__ == "__main__":
    main()