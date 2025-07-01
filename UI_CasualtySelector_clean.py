"""
UI Casualty Selector for Axis & Allies Simulator

This module provides a GUI interface for selecting casualties in battle scenarios
for both land and naval combat in the Axis & Allies board game.
"""

import os
from typing import Union, Dict, List
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Default casualty order for ground units (weakest to strongest)
DEFAULT_LOSS_ORDER_GROUND = [
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

# Default casualty order for naval units
DEFAULT_LOSS_ORDER_NAVAL = [
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

# Available powers/nations in the game
POWERS = [
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


def get_unit_casualties(is_land: bool, current_units: Dict[str, int], num_hits: int, side: str, power: str = "Neutral") -> Dict[str, int]:
    """
    Display a GUI for selecting unit casualties in battle.
    
    Args:
        is_land: True for land battle, False for naval battle
        current_units: Dictionary mapping unit names to their current counts
        num_hits: Number of casualties that must be selected
        side: Name of the side (e.g., "Attacker", "Defender")
        power: Nation/power name for determining unit images (default: "Neutral")
    
    Returns:
        Dictionary mapping unit names to their remaining counts after casualties
    """
    is_naval = not is_land
    
    if is_land:
        unit_dict = {
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
        loss_order = DEFAULT_LOSS_ORDER_GROUND
    else:
        unit_dict = {
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
        loss_order = DEFAULT_LOSS_ORDER_NAVAL
        # Create the "hit" version of 2 HP units for naval combat
        current_units["carrier_hit"] = (
            current_units.get("carrier_hit", 0) + current_units["carrier"]
        )
        current_units["battleship_hit"] = (
            current_units.get("battleship_hit", 0) + current_units["battleship"]
        )
    
    UNIT_COUNT = len(unit_dict)

    def get_file_paths(directory: str) -> Dict[str, str]:
        """Get all file paths in a directory as a dictionary."""
        file_dict = {}
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_dict[filename] = file_path
        return file_dict
    
    image_file_dict = get_file_paths(f".\\Resources\\{power}")

    # Create the main window
    root_cas = tk.Tk()
    root_cas.title("Casualty Selection")

    def select_all(event: tk.Event):
        """Select all text in a spinbox when it gains focus."""
        widget: tk.Spinbox = event.widget
        widget.selection_range(0, tk.END)

    # Initialize UI component lists and dictionaries
    spinboxes = [None for _ in range(UNIT_COUNT)]
    spinbox_dict = {}
    spinbox_vals = [None for _ in range(UNIT_COUNT)]
    casualty_labels = [None for _ in range(UNIT_COUNT)]
    casualty_vals = [None for _ in range(UNIT_COUNT)]
    casualty_val_dict = {}
    spinbox_val_dict = {}

    main_lbl_var = tk.StringVar(value=f"{side}: Select 0 more casualties (of {num_hits})")
    label = tk.Label(root_cas, font=("Arial", 14), textvariable=main_lbl_var)
    label.grid(row=0, columnspan=UNIT_COUNT, pady=10)

    # Lists to store image references (prevents garbage collection)
    images = []
    photos = []

    def update_main_label():
        """Update the main label showing remaining casualties to select."""
        remaining = left_to_select()
        main_lbl_var.set(f"Select {remaining} more casualties (of {num_hits})")

    def left_to_select() -> int:
        """Calculate how many more casualties need to be selected."""
        return num_hits - get_total_casualties()

    def get_units_left(unit: str) -> int:
        """Get the number of units remaining for a given unit type."""
        return int(casualty_val_dict[unit].get())

    def num_units_lost(unit: str) -> int:
        """Get the number of units lost for a given unit type."""
        return spinbox_val_dict[unit].get()

    def assign_default_casualties(num_hits: int):
        """Automatically assign casualties based on default loss order."""
        assigned_hits = 0
        for unit in loss_order:
            units_left = get_units_left(unit)
            while units_left > 0 and assigned_hits < num_hits:
                lose_unit(unit)
                assigned_hits += 1
                units_left = get_units_left(unit)
            if assigned_hits >= num_hits:
                break

    def get_total_casualties() -> int:
        """Calculate total casualties selected."""
        original_unit_count = sum(current_units.values())
        new_unit_count = sum([int(i.get()) for i in casualty_vals])
        return original_unit_count - new_unit_count

    def lose_unit(unit: str):
        """Mark one unit as a casualty."""
        if left_to_select() == 0:
            return
            
        # Get tkinter variables
        lost_var = spinbox_val_dict[unit]
        lost_units = num_units_lost(unit)

        # Get literal values
        remaining_var = casualty_val_dict[unit]
        remaining_units = get_units_left(unit)

        # If no units left, do nothing
        if remaining_units == 0:
            return

        # Update labels
        lost_var.set(lost_units + 1)
        remaining_var.set(str(remaining_units - 1))
        update_main_label()

    def unlose_unit(unit: str):
        """Remove one unit from casualties (bring it back)."""
        original_count = current_units[unit]
        current_count = get_units_left(unit)
        lost_unit_count = num_units_lost(unit)

        if current_count == original_count:
            return

        lost_var = spinbox_val_dict[unit]
        remaining_var = casualty_val_dict[unit]
        lost_var.set(lost_unit_count - 1)
        remaining_var.set(str(current_count + 1))
        update_main_label()

    def get_old_spinbox_value(unit: Union[int, str]) -> int:
        """Get the previous value of a spinbox before user interaction."""
        if isinstance(unit, int):
            unit = unit_dict[unit]
        original_count = current_units[unit]
        remaining = get_units_left(unit)
        lost = original_count - remaining
        return lost

    def spinbox_button_press(spinbox_num: int, value: int):
        """Handle spinbox arrow button presses."""
        # Get old value
        unit = unit_dict[spinbox_num]
        lost = get_old_spinbox_value(unit)
        
        if lost == (value + 1):
            spinbox_val_dict[unit].set(lost)
            unlose_unit(unit)
        elif lost == (value - 1):
            spinbox_val_dict[unit].set(lost)
            lose_unit(unit)
        elif lost == 0 and value == 0:
            return
        else:
            messagebox.showerror("Error", "Unhandled case with spinbox button press")
            raise Exception("Unexpected spinbox state")

    def get_unit_image(unit_index: Union[int, str]) -> Image.Image:
        """Load and return the image for a unit type."""
        if isinstance(unit_index, int):
            unit_index = unit_dict[unit_index]
        image = Image.open(image_file_dict[unit_index + ".png"])
        # FIXME: Memory leak - this array will grow indefinitely
        images.append(image)
        return image

    def spinbox_focus_out(event: tk.Event):
        """Handle when user finishes editing a spinbox value."""
        spinbox = event.widget
        unit_index = spinbox_dict[spinbox]
        
        # Check if value was updated
        old_val = get_old_spinbox_value(unit_index)
        unit = unit_dict[unit_index]
        int_var = spinbox_val_dict[unit]
        
        if int_var.get() == old_val:
            return  # Nothing changed, nothing to do

        # Safeguard against invalid values
        if int_var.get() < 0:
            int_var.set(0)
        if int_var.get() > current_units[unit]:
            int_var.set(current_units[unit])

        # Lose/unlose units as needed
        delta = int_var.get() - old_val
        if delta > 0:
            int_var.set(old_val)
            for _ in range(delta):
                lose_unit(unit)
        elif delta < 0:
            delta = abs(delta)
            int_var.set(old_val)
            for _ in range(delta):
                unlose_unit(unit)

    # Create UI components for each unit type
    for col in range(UNIT_COUNT):
        unit_name = unit_dict[col]
        unit_count = current_units[unit_name]
        
        # Current unit count label (top)
        top_label = tk.Label(root_cas, text=str(unit_count), font=("Arial", 14))
        top_label.grid(row=2, column=col, padx=5, pady=5)
        
        # Spinbox for selecting casualties
        var = tk.IntVar(value=0)
        spinbox_val_dict[unit_name] = var
        spinbox_vals[col] = var
        
        spinbox = tk.Spinbox(
            root_cas,
            from_=0,
            to=10000,
            width=5,
            font=("Arial", 14),
            textvariable=var,
            command=lambda i=col: spinbox_button_press(i, spinbox_vals[i].get()),
        )
        spinbox.grid(row=3, column=col, padx=5, pady=5)
        spinbox.bind("<FocusIn>", select_all)
        spinbox.bind("<FocusOut>", spinbox_focus_out)
        spinboxes[col] = spinbox
        spinbox_dict[spinbox] = col

        # Unit image
        image = get_unit_image(col)
        images.append(image)
        photo = ImageTk.PhotoImage(image)
        photos.append(photo)
        image_label = tk.Label(root_cas, image=photo)
        image_label.grid(row=1, column=col, padx=5, pady=5)
        
        # Remaining unit count label (bottom)
        str_var = tk.StringVar(value=str(unit_count))
        bottom_label = tk.Label(root_cas, textvariable=str_var, font=("Arial", 14))
        bottom_label.grid(row=4, column=col, padx=5, pady=5)
        casualty_labels[col] = bottom_label
        casualty_vals[col] = str_var
        casualty_val_dict[unit_name] = str_var
        
        # Hide components for units with 0 count
        if unit_count == 0:
            top_label.grid_forget()
            image_label.grid_forget()
            spinbox.grid_forget()
            bottom_label.grid_forget()

    # Assign default casualties automatically
    assign_default_casualties(num_hits)

    # Determine if user interaction is needed
    number_of_distinct_units = len([count for count in current_units.values() if count > 0])
    subs_present = is_naval and current_units.get("submarine", 0) > 0
    
    if number_of_distinct_units > 1 or subs_present:
        # Create a Submit button
        submit_button = tk.Button(
            root_cas, text="Submit", command=root_cas.destroy, font=("Arial", 14)
        )
        root_cas.bind("<Return>", lambda e: root_cas.destroy())
        submit_button.grid(row=9, columnspan=UNIT_COUNT // 2, pady=10)

        # Start the Tkinter event loop
        root_cas.mainloop()
    else:
        root_cas.destroy()

    # Calculate final results
    result = {}
    if is_naval:  # Correct damaged battleship and carrier numbers
        battleships = get_units_left("battleship")
        current_units["battleship_hit"] = current_units["battleship_hit"] - battleships
        carriers = get_units_left("carrier")
        current_units["carrier_hit"] = current_units["carrier_hit"] - carriers
        
    for unit, var in spinbox_val_dict.items():
        result[unit] = current_units[unit] - var.get()

    return result


if __name__ == "__main__":
    # Test data for naval battle
    test_units = {
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
    print("Initial units:", test_units)
    
    # Test the casualty selection
    remaining_units = get_unit_casualties(False, test_units, 4, "Defender", "Germans")
    print("Remaining units:", remaining_units)
