import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk

defaultLossOrder_Ground = ["conscript",
                           "aaGun",
                           "infantry",
                           "mech_infantry",
                           "artillery",
                           "armour",
                           "fighter",
                           "tactical_bomber",
                           "bomber",
                           ]


class Combatant:
    def __init__(self, power: str, units: dict[str, dict[str:int]]):
        self.power = power
        self.units = units

    def __str__(self):
        return self.power + "\n" + str(self.units)


def GetUnitCasualties(isLand: bool, currentUnits: dict[str:int], numHits):
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
        for x, y in returnDict.items():
            for k, v in y.items():
                v.set(0)

    imageFileDict = get_file_paths(imagesDirectory)

    # Create the main window
    root = tk.Tk()
    root.title("Spinbox Grid")

    def select_all(event: tk.Event):
        wid: tk.Spinbox = event.widget
        wid.selection_range(0, tk.END)

    # Create a 2D list to hold Spinbox widgets
    spinboxes = [None for _ in range(UNITCOUNT)]
    spinboxVals = [None for _ in range(UNITCOUNT)]
    casualtyLabels = [None for _ in range(UNITCOUNT)]
    casualtyVals = [None for _ in range(UNITCOUNT)]
    casualtyValDict = {}
    returnDict = {}

    label = tk.Label(root, font=("Arial", 14), text="Select Casualties")
    label.grid(row=0, columnspan=UNITCOUNT, pady=10)

    images = []
    photos = []

    label = "attacker"
    spinboxValDict = {}

    def getUnitsLeft(unit:str):
        return int(casualtyValDict[unit].get())

    def numUnitsLost(unit:str):
        return spinboxValDict[unit].get()

    def assignDefaultCasualties(numHits):
        assignedHits = 0
        for unit in defaultLossOrder_Ground:
            unitsLeft = getUnitsLeft(unit)
            while unitsLeft > 0 and assignedHits < numHits:
                loseUnit(unit)
                assignedHits += 1
                unitsLeft = getUnitsLeft(unit)
            if assignedHits >= numHits:
                break



    def getTotalCasualties():
        origUnitCnt = sum(currentUnits.values())
        newUnitCnt = sum([int(i.get()) for i in casualtyVals])
        return origUnitCnt - newUnitCnt

    def loseUnit(unit):
        print(f"Losing {unit}")
        # Get tk vars
        lostVar = spinboxValDict[unit]
        lostUnits = numUnitsLost(unit)

        # Get literal values
        remainingVar = casualtyValDict[unit]
        remainingUnits = getUnitsLeft(unit)

        # If no units left, do nothing
        if remainingUnits == 0:
            return
        
        # Update labels
        lostVar.set(lostUnits + 1)
        remainingVar.set(str(remainingUnits - 1))

    def unloseUnit(unit):
        print(f"Unlosing {unit}")
        originalCnt = currentUnits[unit]
        currentCnt = getUnitsLeft(unit)
        lostUnitCnt = numUnitsLost(unit)

        if currentCnt == originalCnt:
            return
        
        lostVar = spinboxValDict[unit]
        remainingVar = casualtyValDict[unit]
        lostVar.set(lostUnitCnt - 1)
        remainingVar.set(str(currentCnt + 1))

    def updateCasualtyLabel(spinboxNum, value):
        # Get old value
        unit = unitDict[spinboxNum]
        originalCnt = currentUnits[unit]
        remaining = getUnitsLeft(unit)
        lost = originalCnt - remaining
        if lost == (value + 1):
            spinboxValDict[unit].set(lost)
            unloseUnit(unit)
        elif lost == (value - 1):
            spinboxValDict[unit].set(lost)
            loseUnit(unit)
        else:
            raise Exception("Whoopsie")
        
        # val = currentUnits[unitDict[spinboxNum]]
        # newVal = val - int(value)
        # # Validate
        # if newVal < 0:
        #     spinboxVals[spinboxNum].set(spinboxVals[spinboxNum].get() - 1)
        #     newVal = 0
        # casualtyVals[spinboxNum].set(f"{newVal}")
        # print(getTotalCasualties())

    for col in range(UNITCOUNT):
        # Current unit counts
        lbl = tk.Label(root, text=str(
            currentUnits[unitDict[col]]), font=('Arial', 14))
        lbl.grid(row=2, column=col, padx=5, pady=5)
        # Spin Boxes
        var = tk.IntVar(value=0)
        spinboxValDict[unitDict[col]] = var
        spinboxVals[col] = var
        spinboxes[col] = tk.Spinbox(
            root, from_=0, to=100, width=5, font=('Arial', 14), textvariable=var, command=lambda i=col: updateCasualtyLabel(i, spinboxVals[i].get()))
        spinboxes[col].grid(row=3, column=col, padx=5, pady=5)
        spinboxes[col].bind("<FocusIn>", select_all)
        # Override arrow behavior

        # Images
        image = Image.open(imageFileDict[unitDict[col] + ".png"])
        images.append(image)
        photo = ImageTk.PhotoImage(image)
        photos.append(photo)
        lbl = tk.Label(root, image=photo)
        # spinboxes[row][col] = tk.Label(root, text="Hello " + str(col), font=("arial",10))
        lbl.grid(row=1, column=col, padx=5, pady=5)

        strVar = tk.StringVar(value=str(currentUnits[unitDict[col]]))
        lbl = tk.Label(root, textvariable=strVar, font=('Arial', 14))
        lbl.grid(row=4, column=col, padx=5, pady=5)
        casualtyLabels[col] = lbl
        casualtyVals[col] = strVar
        casualtyValDict[unitDict[col]] = strVar

    assignDefaultCasualties(numHits)

    # Create a Submit button
    submit_button = tk.Button(
        root, text="Submit", command=root.destroy, font=('Arial', 14))
    submit_button.grid(row=9, columnspan=UNITCOUNT//2, pady=10)
    resetButton = tk.Button(
        root, text="Reset", command=resetBoxes, font=('Arial', 14))
    resetButton.grid(row=9, columnspan=UNITCOUNT//2,
                     pady=10, column=UNITCOUNT//2)

    # Start the Tkinter event loop
    root.mainloop()

    # # Retrieve values from Spinboxes and store them in a 2D list
    # values = [[returnDict[row][col].get() for col in range(UNITCOUNT)]
    #         for row in range(2)]
    # # Show the collected values in a message box
    # messagebox.showinfo("Submitted Values", str(values))
    rv = {}
    for side, dic in returnDict.items():
        valDict = {}
        for key, value in dic.items():
            valDict[key] = value.get()
        rv[side] = Combatant(var1.get(), valDict)

    return rv


if __name__ == "__main__":
    currentUnits = {
        "infantry": 2,
        "mech_infantry": 1,
        "artillery": 2,
        "armour": 5,
        "fighter": 3,
        "tactical_bomber": 1,
        "bomber": 2,
        "aaGun": 0,
        "conscript": 0,
        "cruiser": 0,
        "battleship": 0,
    }
    vals = GetUnitCasualties(True, currentUnits, 3)

    print(vals)
