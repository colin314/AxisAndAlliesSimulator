from logging import root
from typing import Union
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
    window.geometry(f"+{x}+{y}")

defaultLossOrder_Ground = [
    "conscript",
    "aaGun",
    "infantry",
    "mech_infantry",
    "artillery",
    "armour",
    "fighter",
    "tactical_bomber",
    "bomber",
]

defaultLossOrder_Naval = [
    "battleship",
    "carrier",
    "submarine",
    "destroyer",
    "cruiser",
    "fighter",
    "tactical_bomber",
    "bomber",
    "carrier_hit",
    "battleship_hit",
]

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

def GetUnitCasualties(isLand: bool, currentUnits: dict[str:int], numHits, side:str, power:str="Neutral"):
    isNaval = not isLand
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
        }
        lossOrder = defaultLossOrder_Ground
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
        }
        lossOrder = defaultLossOrder_Naval
        # Just create the "hit" version of 2 HP units
        currentUnits["carrier_hit"] = (
            ( currentUnits["carrier_hit"] if "carrier_hit" in currentUnits.keys() else 0) + currentUnits["carrier"]
        )
        currentUnits["battleship_hit"] = (
            (currentUnits["battleship_hit"] if "battleship_hit" in currentUnits.keys() else 0) + currentUnits["battleship"]
        )
    UNITCOUNT = len(unitDict)


    def get_file_paths(directory):
        file_dict = {}
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_dict[filename] = file_path
        return file_dict
    
    imageFileDict = get_file_paths(".\\Resources\\" + power)

    def resetBoxes():
        for x, y in returnDict.items():
            for k, v in y.items():
                v.set(0)

    # Create the main window
    rootCas = tk.Tk()
    rootCas.title("Spinbox Grid")

    def select_all(event: tk.Event):
        wid: tk.Spinbox = event.widget
        wid.selection_range(0, tk.END)

    # Create a 2D list to hold Spinbox widgets
    spinboxes = [None for _ in range(UNITCOUNT)]
    spinboxDict = {}
    spinboxVals = [None for _ in range(UNITCOUNT)]
    casualtyLabels = [None for _ in range(UNITCOUNT)]
    casualtyVals = [None for _ in range(UNITCOUNT)]
    casualtyValDict = {}
    returnDict = {}

    mainLblVar = tk.StringVar(value=f"{side}: Select {numHits} casualties (0 remaining)")
    label = tk.Label(rootCas, font=("Arial", 14), textvariable=mainLblVar)
    label.grid(row=0, columnspan=UNITCOUNT, pady=10)

    images = []
    photos = []

    label = "attacker"
    spinboxValDict = {}

    def updateMainLbl():
        totalCasualties = getTotalCasualties()
        mainLblVar.set(f"Select {numHits} casualties ({leftToSelect()} remaining)")

    def leftToSelect():
        return numHits - getTotalCasualties()

    def getUnitsLeft(unit: str):
        return int(casualtyValDict[unit].get())

    def numUnitsLost(unit: str):
        return spinboxValDict[unit].get()

    def assignDefaultCasualties(numHits):
        assignedHits = 0
        for unit in lossOrder:
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
        if leftToSelect() == 0:
            return
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
        updateMainLbl()

    def unloseUnit(unit):
        originalCnt = currentUnits[unit]
        currentCnt = getUnitsLeft(unit)
        lostUnitCnt = numUnitsLost(unit)

        if currentCnt == originalCnt:
            return

        lostVar = spinboxValDict[unit]
        remainingVar = casualtyValDict[unit]
        lostVar.set(lostUnitCnt - 1)
        remainingVar.set(str(currentCnt + 1))
        updateMainLbl()

    def getOldSpinboxVal(unit: Union[int, str]):
        if isinstance(unit, int):
            unit = unitDict[unit]
        originalCnt = currentUnits[unit]
        remaining = getUnitsLeft(unit)
        lost = originalCnt - remaining
        return lost

    def spinboxButtonPress(spinboxNum, value):
        # Get old value
        unit = unitDict[spinboxNum]
        lost = getOldSpinboxVal(unit)
        if lost == (value + 1):
            spinboxValDict[unit].set(lost)
            unloseUnit(unit)
        elif lost == (value - 1):
            spinboxValDict[unit].set(lost)
            loseUnit(unit)
        elif lost == 0 and value == 0:
            return
        else:
            messagebox.showerror("Error", "Unhandled case with spinbox button press")
            raise Exception("Whoopsie")

    def getUnitImage(i):
        if isinstance(i,int):
            i = unitDict[i]
        image = Image.open(imageFileDict[i + ".png"])
        #FIXME: Memory leak, this array will just grow and grow
        images.append(image)
        return image

    def spinboxFocusOut(event):
        spinbox = event.widget
        i = spinboxDict[spinbox]
        # Check if val was updated
        oldVal = getOldSpinboxVal(i)
        unit = unitDict[i]
        intVar = spinboxValDict[unit]
        if intVar.get() == oldVal:
            return  # Nothing changed, nothing to do

        # Safeguard against too high or too low values
        if intVar.get() < 0:
            intVar.set(0)
        if intVar.get() > currentUnits[unit]:
            intVar.set(currentUnits[unit])

        # Lose/Unlose units as needed
        delta = intVar.get() - oldVal
        if delta > 0:
            intVar.set(oldVal)
            for j in range(delta):
                loseUnit(unit)
        if delta < 0:
            delta = abs(delta)
            intVar.set(oldVal)
            for j in range(delta):
                unloseUnit(unit)

    for col in range(UNITCOUNT):
        # Current unit counts
        topLbl = tk.Label(rootCas, text=str(currentUnits[unitDict[col]]), font=("Arial", 14))
        topLbl.grid(row=2, column=col, padx=5, pady=5)
        # Spin Boxes
        var = tk.IntVar(value=0)
        spinboxValDict[unitDict[col]] = var
        spinboxVals[col] = var
        spinbox = tk.Spinbox(
            rootCas,
            from_=0,
            to=10000,
            width=5,
            font=("Arial", 14),
            textvariable=var,
            command=lambda i=col: spinboxButtonPress(i, spinboxVals[i].get()),
        )
        spinbox.grid(row=3, column=col, padx=5, pady=5)
        spinbox.bind("<FocusIn>", select_all)
        spinbox.bind("<FocusOut>", spinboxFocusOut)
        spinboxes[col] = spinbox
        spinboxDict[spinbox] = col
        # Override arrow behavior

        # Images
        image = getUnitImage(col)
        images.append(image)
        photo = ImageTk.PhotoImage(image)
        photos.append(photo)
        imageLbl = tk.Label(rootCas, image=photo)
        # spinboxes[row][col] = tk.Label(rootCas, text="Hello " + str(col), font=("arial",10))
        imageLbl.grid(row=1, column=col, padx=5, pady=5)
        

        strVar = tk.StringVar(value=str(currentUnits[unitDict[col]]))
        botLbl = tk.Label(rootCas, textvariable=strVar, font=("Arial", 14))
        botLbl.grid(row=4, column=col, padx=5, pady=5)
        casualtyLabels[col] = botLbl
        casualtyVals[col] = strVar
        casualtyValDict[unitDict[col]] = strVar
        
        if currentUnits[unitDict[col]] == 0:
            topLbl.grid_forget()
            imageLbl.grid_forget()
            spinbox.grid_forget()
            botLbl.grid_forget()

    assignDefaultCasualties(numHits)

    numberOfDistinctUnits = len([i for i in currentUnits.values() if i > 0])
    subsPresent = isNaval and currentUnits["submarine"] > 0
    if numberOfDistinctUnits > 1 or subsPresent:
        # Create a Submit button
        submit_button = tk.Button(
            rootCas, text="Submit", command=rootCas.destroy, font=("Arial", 14)
        )
        rootCas.bind("<Return>",lambda e:rootCas.destroy())
        submit_button.grid(row=9, columnspan=UNITCOUNT // 2, pady=10)

        # Start the Tkinter event loop
        center_window_left_half(rootCas)
        rootCas.after(1, lambda: submit_button.focus_force())
        rootCas.mainloop()
    else:
        rootCas.destroy()

    rv = {}
    if isNaval:  # Correct damaged battleship and carrier numbers
        battleships = getUnitsLeft("battleship")
        currentUnits["battleship_hit"] = currentUnits["battleship_hit"] - battleships
        carriers = getUnitsLeft("carrier")
        currentUnits["carrier_hit"] = currentUnits["carrier_hit"] - carriers
    for unit, var in spinboxValDict.items():
        rv[unit] = currentUnits[unit] - var.get()

    return rv


if __name__ == "__main__":
    # currentUnits = {
    #     "infantry": 60,
    #     "mech_infantry": 16,
    #     "artillery": 300,
    #     "armour": 5000,
    #     "fighter": 3,
    #     "tactical_bomber": 1,
    #     "bomber": 2,
    #     "aaGun": 5,
    #     "conscript": 500,
    #     "cruiser": 0,
    #     "battleship": 0,
    # }
    currentUnits = {
        "submarine": 2,
        "destroyer": 1,
        "cruiser": 1,
        "battleship": 2,
        "carrier": 2,
        "fighter": 1,
        "tactical_bomber": 1,
        "bomber": 1,
        "battleship_hit": 0,
        "carrier_hit": 0,
        "transport": 0,
    }
    print(currentUnits)
    vals = GetUnitCasualties(False, currentUnits, 4)
    print(vals)
