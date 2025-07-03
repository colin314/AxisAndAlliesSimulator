from logging import root
from typing import Union
import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk
from Config import Config

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

class CasualtyUI:
    def __init__(self, isLand: bool, currentUnits: dict[str:int], power:str="Neutral"):
        self.isLand = isLand
        self.currentUnits = currentUnits
        self.power = power
        self.spinboxes: list[tk.Spinbox] = []
        self.spinboxVals: list[tk.IntVar] = []
        self.spinboxDict: dict[str, tk.Spinbox] = {}
        self.remainingUnitCountLabels: list[tk.Label] = []
        self.remainingUnitCountVals: list[tk.StringVar] = []
        self.remainingUnitCountValDict: dict[str, tk.StringVar] = {}

    def GetUnitCasualties(self, numHits:int, side:str, manualMode:bool=False):
        isNaval = not self.isLand
        if self.isLand:
            unitDict = Config.landUnitDict
            lossOrder = Config.defaultLossOrder_Ground
        else:
            unitDict = Config.navalUnitDict
            lossOrder = Config.defaultLossOrder_Naval
            # To make sure the "hit" version of 2 HP units show up, Just create the "hit" version of 2 HP units. They will be removed later
            currentUnits["carrier_hit"] = (
                ( currentUnits["carrier_hit"] if "carrier_hit" in currentUnits.keys() else 0) + currentUnits["carrier"]
            )
            currentUnits["battleship_hit"] = (
                (currentUnits["battleship_hit"] if "battleship_hit" in currentUnits.keys() else 0) + currentUnits["battleship"]
            )
        UNITCOUNT = len(unitDict)

        imageFileDict = CasualtyUI.get_file_paths(".\\Resources\\" + self.power)

        # Create the main window
        rootCas = tk.Tk()
        rootCas.title("Spinbox Grid")

        def select_all(event: tk.Event):
            wid: tk.Spinbox = event.widget
            wid.selection_range(0, tk.END)

        # Create a 2D list to hold Spinbox widgets
        self.initS

        mainLabelVar = tk.StringVar(value=f"{side}: Select {numHits} casualties ({numHits if manualMode else 0} remaining)")
        mainLabel = tk.mainLabel(rootCas, font=("Arial", 14), textvariable=mainLabelVar)
        mainLabel.grid(row=0, columnspan=UNITCOUNT, pady=10)

        images = []
        photos = []

        mainLabel = "attacker"
        spinboxValDict: dict[str, tk.IntVar] = {}

        def updateMainLbl():
            mainLabelVar.set(f"Select {numHits} casualties ({leftToSelect()} remaining)")

        def leftToSelect() -> int:
            return numHits - getTotalCasualties()

        def getUnitsLeft(unit: str) -> int:
            return int(self.remainingUnitCountValDict[unit].get())

        def numUnitsLost(unit: str) -> int:
            return spinboxValDict[unit].get()

        def assignDefaultCasualties(numHits: int):
            assignedHits = 0
            for unit in lossOrder:
                unitsLeft = getUnitsLeft(unit)
                while unitsLeft > 0 and assignedHits < numHits:
                    loseUnit(unit)
                    assignedHits += 1
                    unitsLeft = getUnitsLeft(unit)
                if assignedHits >= numHits:
                    break

        def getTotalCasualties() -> int:
            origUnitCnt = sum(currentUnits.values())
            newUnitCnt = sum([int(i.get()) for i in self.remainingUnitCountVals])
            return origUnitCnt - newUnitCnt

        def handleHitTo2HPUnit(hitUnit: str):
            """Create a "hit" version of a 2 HP unit when the unit takes a hit."""
            # Update the "original" unit_hit count
            currentUnits[hitUnit] = currentUnits[hitUnit] + 1
            # Update the spinbox value (No need, since it's not lost)
            # Update the remaining count label
            remainingVar = self.remainingUnitCountValDict[hitUnit]
            remainingVar.set(str(getUnitsLeft(hitUnit) + 1))

        def loseUnit(unit:str):
            if leftToSelect() == 0:
                return
            # Get tk vars
            lostVar = spinboxValDict[unit]
            lostUnits = numUnitsLost(unit)

            # Get literal values
            remainingVar = self.remainingUnitCountValDict[unit]
            remainingUnits = getUnitsLeft(unit)

            # If no units left, do nothing
            if remainingUnits == 0:
                return

            # Update labels
            lostVar.set(lostUnits + 1)
            remainingVar.set(str(remainingUnits - 1))
            updateMainLbl()

            # Account for 2 HP units
            if unit == "carrier":
                handleHitTo2HPUnit("carrier_hit")
            elif unit == "battleship":
                handleHitTo2HPUnit("battleship_hit")

        def unhandleHitTo2HPUnit(unit: str, hitUnit: str):
            # Get number of carrier_hit that have been lost (above the original count)
            # Number of carrier_hits (original) minus the number of carriers that have been assigned a hit
            carriersAssignedHitsCnt = numUnitsLost(unit)
            # The number of carrier_hit created by losing carriers is equal to the number of carrier_hit that currently exist minus the number of carrier that have been assigned hits.
            hitCarriersRemainingCnt = int(self.remainingUnitCountValDict[hitUnit].get())
            if hitCarriersRemainingCnt <= 0: # carrier_hit need to be un-lost first
                unloseUnit(hitUnit)
            # Update the "original" carrier_hit count
            currentUnits[hitUnit] = currentUnits[hitUnit] - 1
            # Update the spinbox value (No need, since it's not lost)
            # Update the remaining count label
            remainingVar = self.remainingUnitCountValDict[hitUnit]
            remainingVar.set(str(getUnitsLeft(hitUnit) - 1))

        def unloseUnit(unit):
            originalCnt = currentUnits[unit]
            currentCnt = getUnitsLeft(unit)
            lostUnitCnt = numUnitsLost(unit)

            if currentCnt == originalCnt:
                return

            # To unlose a 2 HP unit, we can't have lost the hit version of the unit.
            # If there are no "hit" versions of the unit to recover, we need to quit
            if unit == "carrier":
                unhandleHitTo2HPUnit("carrier", "carrier_hit")
            elif unit == "battleship":
                unhandleHitTo2HPUnit("battleship", "battleship_hit")

            lostVar = spinboxValDict[unit]
            remainingVar = self.remainingUnitCountValDict[unit]
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
            i = self.spinboxDict[spinbox]
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
            # Spin Boxes
            var = tk.IntVar(value=0)
            spinboxValDict[unitDict[col]] = var
            self.spinboxVals[col] = var
            spinbox = tk.Spinbox(
                rootCas,
                from_=0,
                to=10000,
                width=2,
                font=("Arial", 24),
                textvariable=var,
                command=lambda i=col: spinboxButtonPress(i, self.spinboxVals[i].get()),
            )
            spinbox.grid(row=3, column=col, padx=5, pady=5)
            spinbox.bind("<FocusIn>", select_all)
            spinbox.bind("<FocusOut>", spinboxFocusOut)
            self.spinboxObjArr[col] = spinbox
            self.spinboxDict[spinbox] = col

            # Images
            image = getUnitImage(col)
            images.append(image)
            photo = ImageTk.PhotoImage(image)
            photos.append(photo)
            imageLbl = tk.Label(rootCas, image=photo)
            imageLbl.grid(row=1, column=col, padx=5, pady=5)

            strVar = tk.StringVar(value=str(currentUnits[unitDict[col]]))
            botLbl = tk.Label(rootCas, textvariable=strVar, font=("Arial", 24))
            botLbl.grid(row=2, column=col, padx=5, pady=5)
            self.remainingUnitCountLabels[col] = botLbl
            self.remainingUnitCountVals[col] = strVar
            self.remainingUnitCountValDict[unitDict[col]] = strVar
            
            if currentUnits[unitDict[col]] == 0:
                imageLbl.grid_forget()
                spinbox.grid_forget()
                botLbl.grid_forget()

        # Remove the extra "hit" version of 2 HP units that were added earlier
        if isNaval:
            # carrier
            currentUnits["carrier_hit"] = currentUnits["carrier_hit"] - currentUnits["carrier"]
            self.remainingUnitCountValDict["carrier_hit"].set(currentUnits["carrier_hit"])

            # battleship
            currentUnits["battleship_hit"] = currentUnits["battleship_hit"] - currentUnits["battleship"]
            self.remainingUnitCountValDict["battleship_hit"].set(currentUnits["battleship_hit"])

        if not manualMode:
            assignDefaultCasualties(numHits)
        else:
            # Hacky way to make sure UI is updated with no weird spacing.
            # There is weird spacing (likely from non-existent unit images) until the first time labels are updated
            for unit in lossOrder:
                unitsLeft = getUnitsLeft(unit)
                if unitsLeft > 0:
                    loseUnit(unit)
                    unloseUnit(unit)
                    break

        numberOfDistinctUnits = len([i for i in currentUnits.values() if i > 0])
        subsPresent = isNaval and currentUnits["submarine"] > 0

        if manualMode or numberOfDistinctUnits > 1 or subsPresent:
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
        for unit, var in spinboxValDict.items():
            rv[unit] = currentUnits[unit] - var.get()

        return rv

    def get_file_paths(directory):
        file_dict = {}
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_dict[filename] = file_path
        return file_dict
    
    def initSpinBoxes(self, UNITCOUNT: int, unitDict: dict[int, str]):
        self.spinboxObjArr = [None for _ in range(UNITCOUNT)]
        self.spinboxDict.clear()
        self.spinboxVals = [None for _ in range(UNITCOUNT)]
        self.remainingUnitCountLabels = [None for _ in range(UNITCOUNT)]
        self.remainingUnitCountVals = [None for _ in range(UNITCOUNT)]
        self.remainingUnitCountValDict.clear()

if __name__ == "__main__":
    currentUnits = {
        "submarine": 2,
        "destroyer": 1,
        "cruiser": 1,
        "battleship": 2,
        "carrier": 2,
        "fighter": 1,
        "tactical_bomber": 1,
        "bomber": 1,
        "battleship_hit": 1,
        "carrier_hit": 1,
        "transport": 0,
    }
    print(currentUnits)
    vals = CasualtyUI(False, currentUnits, "Germans").GetUnitCasualties(6, "Attacker")
    print(vals)
