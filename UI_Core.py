import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk
from Simulator import Simulator,GetUnitList
from UnitCollection import UnitCollection
from subprocess import Popen

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

    # Start the Tkinter event loop
    core.mainloop()




if __name__ == "__main__":
    MainLoop()
