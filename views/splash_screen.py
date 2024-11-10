import tkinter as tk

class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.splash = tk.Toplevel()
        self.splash.title("Loading...")
        self.splash.geometry("400x300")
        self.splash.overrideredirect(True)

        # Center the splash screen
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        splash_width = 400
        splash_height = 300
        x = (screen_width // 2) - (splash_width // 2)
        y = (screen_height // 2) - (splash_height // 2)
        self.splash.geometry(f"{splash_width}x{splash_height}+{x}+{y}")

        # Main splash text
        splash_label = tk.Label(self.splash, text="Imaging Toolbox lite", font=("Verdana", 16))
        splash_label.pack(expand=True)

        # "v1" label below the "e" in "lite"
        version_label = tk.Label(self.splash, text="v1", font=("Verdana", 8))
        version_label.place(relx=0.77, rely=0.51)  # Adjust the relx and rely to position the "v1" label

        # Add email label at the bottom-right corner
        email_label = tk.Label(self.splash, text="agustinTortolero", font=("Verdana", 8))
        email_label.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

        self.splash.after(3000, self.destroy_splash)  # Show splash screen for 3 seconds

    def destroy_splash(self):
        self.splash.destroy()
        self.root.deiconify()  # Show the main window