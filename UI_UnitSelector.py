import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk

class Combatant:
    def __init__(self,power:str, units:dict[str, dict[str:int]]):
        self.power = power
        self.units = units

    def __str__(self):
        return self.power + "\n" + str(self.units)


def GetUnitList(isLand:bool):
    global root
    imagesDirectory = '.\\Resources\\Neutral'
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
            10: "transport",
        }
    UNITCOUNT = len(unitDict)


    def get_file_paths(directory):
        file_dict = {}
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_dict[filename] = file_path
        return file_dict

    def resetBoxes():
        for row in range(2):
            for col in range(UNITCOUNT):
                spinBoxVals[row][col].set(0)


    imageFileDict = get_file_paths(imagesDirectory)


    def submit_values():
        # Retrieve values from Spinboxes and store them in a 2D list
        values = [[spinBoxVals[row][col].get() for col in range(UNITCOUNT)]
                for row in range(2)]
        # Show the collected values in a message box
        messagebox.showinfo("Submitted Values", str(values))


    # Create the main window
    root = tk.Tk()
    root.title("Spinbox Grid")

    def select_all(event : tk.Event):
        wid:tk.Spinbox = event.widget
        wid.selection_range(0,tk.END)

    # Create a 2D list to hold Spinbox widgets
    spinboxes = [[None for _ in range(UNITCOUNT)] for _ in range(2)]
    spinBoxVals = {}

    label = tk.Label(root, font=("Arial", 14), text="Attacker")
    label.grid(row=0, columnspan=UNITCOUNT, pady=10)
    label = tk.Label(root, font=("Arial", 14), text="Defender")
    label.grid(row=4, columnspan=UNITCOUNT, pady=10)

    images = []
    photos = []

    for row in range(2):
        label = "attacker" if row == 0 else "defender"
        valDict = {}
        for col in range(UNITCOUNT):
            # Spin Boxes
            var = tk.IntVar(value=0)
            valDict[unitDict[col]] = var
            spinboxes[row][col] = tk.Spinbox(
                root, from_=0, to=100, width=5, font=('Arial', 14), textvariable=var)
            spinboxes[row][col].grid(row=row*4+3, column=col, padx=5, pady=5)
            spinboxes[row][col].bind("<FocusIn>", select_all)

            # Images
            image = Image.open(imageFileDict[unitDict[col] + ".png"])
            images.append(image)
            photo = ImageTk.PhotoImage(image)
            photos.append(photo)
            lbl = tk.Label(root, image=photo)
            # spinboxes[row][col] = tk.Label(root, text="Hello " + str(col), font=("arial",10))
            lbl.grid(row=row*4+2, column=col, padx=5, pady=5)
        spinBoxVals[label] = valDict

    def getFlagPhoto(filePath):
        photo = ImageTk.PhotoImage(Image.open(
            r".\Resources\Flags\\" + filePath + ".png"))
        photos.append(photo)
        return photo


    def addPhotoButton(var: tk.StringVar, val: str, row: int, col: int):
        global root
        image = getFlagPhoto(val)
        radio = tk.Radiobutton(root, image=image, variable=var, value=val)
        radio.grid(row=row, column=col, padx=5, pady=5)


    def CreateRadioButtons(var: tk.StringVar, label:str, rowRoot: int, colRoot: int):
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
    var1 = tk.StringVar(value="Germans")  # Default Value
    CreateRadioButtons(var1, "Attacker", 1, 0)

    # Defender Radio Button Selector
    var2 = tk.StringVar(value="Russians")
    CreateRadioButtons(var2, "Defender", 5, 0)

    def submitTest():
        print(var1.get())


    # Create a Submit button
    submit_button = tk.Button(
        root, text="Submit", command=root.destroy, font=('Arial', 14))
    submit_button.grid(row=9, columnspan=UNITCOUNT//2, pady=10)
    resetButton = tk.Button(
        root, text="Reset", command=resetBoxes, font=('Arial', 14))
    resetButton.grid(row=9, columnspan=UNITCOUNT//2, pady=10, column=UNITCOUNT//2)

    # Start the Tkinter event loop
    root.mainloop()

    # # Retrieve values from Spinboxes and store them in a 2D list
    # values = [[spinBoxVals[row][col].get() for col in range(UNITCOUNT)]
    #         for row in range(2)]
    # # Show the collected values in a message box
    # messagebox.showinfo("Submitted Values", str(values))
    rv = {}
    for side,dic in spinBoxVals.items():
        valDict = {}
        for key,value in dic.items():
            valDict[key] = value.get()
        rv[side] = Combatant(var1.get(), valDict)

    return rv

if __name__ == "__main__":
    vals = GetUnitList(False)
    print(vals)
