import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk
from Simulator import Simulator,GetUnitList
from UnitCollection import UnitCollection
from subprocess import Popen

def center_window_left_half(window):
    """Center the window in the left half of the screen"""
    window.update_idletasks()  # Ensure window size is calculated
    
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Get window dimensions
    window_width = window.winfo_reqwidth()
    window_height = window.winfo_reqheight()
    
    # Calculate position for center of left half
    left_half_width = screen_width // 2
    x = (left_half_width - window_width) // 2
    y = (screen_height - window_height) // 2
    
    # Set window position
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

def MainLoop():
    def Battle(isLand:bool):
        p = Popen("")
    def LandBattle():
        p = Popen("LandBattle.bat")
        stdout, stderr = p.communicate()
    def NavalBattle():
        p = Popen("NavalBattle.bat")
        stdout, stderr = p.communicate()
    core = tk.Tk()
    # Create the main window
    core.title("Virtual Battle Tool")
    attackButton = tk.Button(core,text="Land Battle", command=LandBattle, font=("Arial",14))
    attackButton.grid(row=0, column=0,padx=10,pady=10)
    defendButton = tk.Button(core,text="Naval Battle", command=NavalBattle, font=("Arial",14))
    defendButton.grid(row=0,column=1,padx=10,pady=10)
    center_window_left_half(core)

    # Start the Tkinter event loop
    core.after(1, lambda: core.focus_force())
    core.mainloop()




if __name__ == "__main__":
    MainLoop()
