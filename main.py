import tkinter as tk
from tkinter import messagebox

# Function to gather the input values and display them
def submit():
    quantities = {}
    for item in items:
        quantity = entry_vars[item].get()
        quantities[item] = quantity

    # Show the quantities in a message box
    result = "\n".join(f"{item}: {quantity}" for item, quantity in quantities.items())
    messagebox.showinfo("Submitted Quantities", result)

# Function to select all text in the Spinbox
def select_all(event : tk.Event):
    currWid = root.focus_get()
    print("selecting all")
    wid:tk.Spinbox = event.widget
    print("Selecting Text")
    wid.selection_range(0,tk.END)

def focus_out(event: tk.Event):
    wid: tk.Spinbox = event.widget
    print(type(wid.get()))
    print(wid.get())
    if wid.get() == "":
        wid.insert(0,"0")


# Create the main window
root = tk.Tk()
root.title("Specify Quantities with Spinboxes")

# List of 8 different items
items = [
    "Item 1",
    "Item 2",
    "Item 3",
    "Item 4",
    "Item 5",
    "Item 6",
    "Item 7",
    "Item 8"
]

# Dictionary to store Spinbox variables
entry_vars = {}

# Create labels and Spinboxes for each item
for item in items:
    label = tk.Label(root, text=item)
    label.pack()

    entry_var = tk.IntVar(value=0)  # Default value is 0
    entry_vars[item] = entry_var
    
    # Create a Spinbox with increased width and font size
    spinbox = tk.Spinbox(root, from_=0, to=100, textvariable=entry_var, width=5, font=('Arial', 14))
    spinbox.pack()

    # Bind the click event to select all text in the Spinbox
    spinbox.bind("<FocusIn>", select_all)
    spinbox.bind("<FocusOut>", focus_out)

# Create a submit button
submit_button = tk.Button(root, text="Submit", command=submit, font=('Arial', 14))
submit_button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()
