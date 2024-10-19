import tkinter as tk

def set_spinbox_value():
    # Set a specific value in the Spinbox
    spinbox.set(5)  # Set the value to 5 (or any other valid value)

# Create the main window
root = tk.Tk()
root.title("Spinbox Set Value Example")

# Create a Spinbox
spinbox = tk.Spinbox(root, from_=0, to=10)
spinbox.pack(pady=20)

# Create a button to set the Spinbox value
button = tk.Button(root, text="Set Value to 5", command=set_spinbox_value)
button.pack(pady=10)

# Start the main event loop
root.mainloop()
