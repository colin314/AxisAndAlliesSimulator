import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk

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


class Combatant:
    def __init__(self, power: str, units: dict[str, dict[str:int]]):
        self.power = power
        self.units = units

    def __str__(self):
        return self.power + "\n" + str(self.units)

powers = [
              "Americans",
              "ANZAC",
              "British",
              "Chinese",
              "French",
              "Germans",
              "Italians",
              "Japanese",
              "Russians",
              "Neutral"
              ]

def GetUnitList(isLand: bool):
    global root
    imagesDirectory = ".\\Resources\\Neutral"
    if isLand:
        unitDict = {
            0: "infantry",
            1: "mech_infantry",
            2: "artillery",
            3: "armour",
            4: "fighter",
            5: "tactical_bomber",
            6: "bomber",
            7: "aaGun",
            8: "conscript",
            9: "cruiser",
            10: "battleship",
        }
    else:
        unitDict = {
            0: "submarine",
            1: "destroyer",
            2: "cruiser",
            3: "battleship",
            4: "carrier",
            5: "fighter",
            6: "tactical_bomber",
            7: "bomber",
            8: "battleship_hit",
            9: "carrier_hit",
            # 10: "transport",
        }
    UNITCOUNT = len(unitDict)

    # Dictionary unit.png : <image object>
    def getPowerSpecificImageDict(directory):
        file_dict = {}
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                image = Image.open(file_path)
                file_dict[filename] = image
        return file_dict


    def resetBoxes():
        for x, y in spinBoxVals.items():
            for k, v in y.items():
                v.set(0)


    imageDict = {}
    for power in powers:
        imageDict[power] = getPowerSpecificImageDict(".\\Resources\\" + power)

    def submit_values():
        # Retrieve values from Spinboxes and store them in a 2D list
        values = [
            [spinBoxVals[row][col].get() for col in range(UNITCOUNT)]
            for row in range(2)
        ]
        # Show the collected values in a message box
        messagebox.showinfo("Submitted Values", str(values))

    # Create the main window
    root = tk.Tk()
    root.title("Spinbox Grid")

    def select_all(event: tk.Event):
        wid: tk.Spinbox = event.widget
        wid.selection_range(0, tk.END)

    # Create a 2D list to hold Spinbox widgets
    spinboxes = [[None for _ in range(UNITCOUNT)] for _ in range(2)]
    spinBoxVals = {}

    label = tk.Label(root, font=("Arial", 14), text="Attacker")
    label.grid(row=0, columnspan=UNITCOUNT, pady=10)
    label = tk.Label(root, font=("Arial", 14), text="Defender")
    label.grid(row=4, columnspan=UNITCOUNT, pady=10)

    images = []
    photos = []
    photoDict = {}
    photoDict["attacker"] = {}
    photoDict["defender"] = {}

    def getFlagPhoto(filePath):
        photo = ImageTk.PhotoImage(
            Image.open(r".\Resources\Flags\\" + filePath + ".png")
        )
        photos.append(photo)
        return photo

    def refreshImages(var:tk.StringVar, side:int):
        side = "attacker" if side == 0 else "defender"
        for k,v in photoDict[side].items():
            image = imageDict[var.get()][k + ".png"]
            photo = ImageTk.PhotoImage(image)
            photos.append(photo)
            v.config(image=photo)

    def addPhotoButton(var: tk.StringVar, val: str, row: int, col: int):
        global root
        image = getFlagPhoto(val)
        side = 0 if row < 3 else 1
        radio = tk.Radiobutton(root, image=image, variable=var, value=val, command=lambda v=var,s=side:refreshImages(var,side))
        radio.grid(row=row, column=col, padx=5, pady=5)


    def CreateRadioButtons(var: tk.StringVar, label: str, rowRoot: int, colRoot: int):
        addPhotoButton(var, "Germans", rowRoot, colRoot)
        addPhotoButton(var, "Russians", rowRoot, colRoot + 1)
        addPhotoButton(var, "Japanese", rowRoot, colRoot + 2)
        addPhotoButton(var, "Chinese", rowRoot, colRoot + 3)
        addPhotoButton(var, "Americans", rowRoot, colRoot + 4)
        addPhotoButton(var, "British", rowRoot, colRoot + 5)
        addPhotoButton(var, "Italians", rowRoot, colRoot + 6)
        addPhotoButton(var, "ANZAC", rowRoot, colRoot + 7)
        addPhotoButton(var, "French", rowRoot, colRoot + 8)
        addPhotoButton(var, "Neutral", rowRoot, colRoot + 9)

    # Attacker Radio Button Selector
    attPower = tk.StringVar(value="Germans")  # Default Value
    CreateRadioButtons(attPower, "Attacker", 1, 0)

    # Defender Radio Button Selector
    defPower = tk.StringVar(value="Russians")
    CreateRadioButtons(defPower, "Defender", 5, 0)

    for row in range(2):
        label = "attacker" if row == 0 else "defender"
        valDict = {}
        for col in range(UNITCOUNT):
            # Spin Boxes
            var = tk.IntVar(value=0)
            valDict[unitDict[col]] = var
            spinboxes[row][col] = tk.Spinbox(
                root, from_=0, to=100, width=5, font=("Arial", 14), textvariable=var
            )
            spinboxes[row][col].grid(row=row * 4 + 3, column=col, padx=5, pady=5)
            spinboxes[row][col].bind("<FocusIn>", select_all)

            # Images
            image = imageDict[attPower.get() if row==0 else defPower.get()][unitDict[col] + ".png"]
            photo = ImageTk.PhotoImage(image)
            photos.append(photo)
            lbl = tk.Label(root, image=photo)
            # spinboxes[row][col] = tk.Label(root, text="Hello " + str(col), font=("arial",10))
            lbl.grid(row=row * 4 + 2, column=col, padx=5, pady=5)
            photoDict["attacker" if row == 0 else "defender"][unitDict[col]] = lbl
        spinBoxVals[label] = valDict

    # Cause focus to shift to first spinbox when window opens
    root.after(1, lambda: spinboxes[0][0].focus_force())

    # Create a Submit button
    submit_button = tk.Button(
        root, text="Submit", command=root.destroy, font=("Arial", 14)
    )
    submit_button.grid(row=9, columnspan=UNITCOUNT // 2, pady=10)
    resetButton = tk.Button(root, text="Reset", command=resetBoxes, font=("Arial", 14))
    resetButton.grid(row=9, columnspan=UNITCOUNT // 2, pady=10, column=UNITCOUNT // 2)

    center_window_left_half(root)

    # Start the Tkinter event loop
    root.mainloop()

    # # Retrieve values from Spinboxes and store them in a 2D list
    # values = [[spinBoxVals[row][col].get() for col in range(UNITCOUNT)]
    #         for row in range(2)]
    # # Show the collected values in a message box
    # messagebox.showinfo("Submitted Values", str(values))
    rv = {}
    for side, dic in spinBoxVals.items():
        valDict = {}
        for key, value in dic.items():
            valDict[key] = value.get()
        power = attPower.get() if side == "attacker" else defPower.get()
        rv[side] = Combatant(power, valDict)

    return rv


if __name__ == "__main__":
    vals = GetUnitList(False)
    print(vals)
