import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk
from Simulator import Simulator,GetUnitList
from UnitCollection import UnitCollection
from subprocess import Popen

try:
    from UI_BattleRolls import get_battle_rolls_window, show_battle_rolls_window
    GUI_ROLLS_AVAILABLE = True
except ImportError:
    GUI_ROLLS_AVAILABLE = False

def MainLoop():
    def Battle(isLand:bool):
        p = Popen("")
    def LandBattle():
        p = Popen("LandBattle.bat")
        stdout, stderr = p.communicate()
    def NavalBattle():
        p = Popen("NavalBattle.bat")
        stdout, stderr = p.communicate()
    def ShowBattleRolls():
        if GUI_ROLLS_AVAILABLE:
            show_battle_rolls_window()
        else:
            messagebox.showinfo("Not Available", "Battle Rolls GUI is not available.")
    
    core = tk.Tk()
    # Create the main window
    core.title("Virtual Battle Tool")
    attackButton = tk.Button(core,text="Land Battle", command=LandBattle, font=("Arial",14))
    attackButton.grid(row=0, column=0,padx=10,pady=10)
    defendButton = tk.Button(core,text="Naval Battle", command=NavalBattle, font=("Arial",14))
    defendButton.grid(row=0,column=1,padx=10,pady=10)
    
    # Add battle rolls window button
    if GUI_ROLLS_AVAILABLE:
        rollsButton = tk.Button(core,text="Show Battle Rolls", command=ShowBattleRolls, font=("Arial",14))
        rollsButton.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    # Start the Tkinter event loop
    core.mainloop()




if __name__ == "__main__":
    MainLoop()
