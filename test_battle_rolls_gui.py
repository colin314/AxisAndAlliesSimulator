"""
Test script for the new Battle Rolls GUI functionality.

This script demonstrates how the battle rolls are now displayed in a tkinter
window instead of being printed to the console.
"""

import tkinter as tk
from Units import Infantry, Tank, Fighter
from TechMapping import Tech
from UI_BattleRolls import get_battle_rolls_window, clear_battle_rolls
import time

def test_battle_rolls():
    """Test the new battle rolls GUI functionality."""
    
    # Create a root window (hidden)
    root = tk.Tk()
    #root.withdraw()
    
    # Create some test units
    infantry = Infantry(([2], [2]), [])  # Infantry attacks on 2, defends on 2
    tank = Tank(([3], [3]), [])          # Tank attacks on 3, defends on 3
    fighter = Fighter(([3], [4]), [])    # Fighter attacks on 3, defends on 4
    
    # Get the battle rolls window
    window = get_battle_rolls_window()
    window.show()
    
    print("Testing battle rolls GUI...")
    print("A window should appear showing the roll results.")
    
    # Simulate some combat rolls
    print("\nSimulating attacker rolls...")
    infantry.attack("Attacker")
    time.sleep(0.5)
    
    tank.attack("Attacker")
    time.sleep(0.5)
    
    fighter.attack("Attacker")
    time.sleep(0.5)
    
    print("\nSimulating defender rolls...")
    infantry.defend("Defender")
    time.sleep(0.5)
    
    tank.defend("Defender")
    time.sleep(0.5)
    
    fighter.defend("Defender")
    time.sleep(0.5)
    
    print("\nTest complete! Check the GUI window for results.")
    print("Close the GUI window or press Ctrl+C to exit.")
    

    root.mainloop()


if __name__ == "__main__":
    test_battle_rolls()
