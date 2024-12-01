import tkinter as tk
import customtkinter as ctk

class SliderLabelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Slider and Label Example")
        self.root.geometry("300x200")

        # Label to display the slider value
        self.label = ctk.CTkLabel(root, text="Slider Value: 0")
        self.label.pack(pady=20)

        # Slider to change the label content
        self.slider = ctk.CTkSlider(root, from_=0, to=100, command=self.update_label)
        self.slider.pack(pady=20)

    def update_label(self, value):
        # Update label with the slider's current value
        self.label.config(text=f"Slider Value: {int(float(value))}")

# Main window setup
if __name__ == "__main__":
    root = ctk.CTk()  # or tk.Tk() if not using customtkinter
    app = SliderLabelApp(root)
    root.mainloop()
