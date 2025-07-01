"""
Battle Rolls Display for Axis & Allies Simulator.

This module provides a tkinter-based GUI for displaying individual combat
roll results during battle simulation, replacing command-line output with
a visual progress bar representation.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class RollResult:
    """Data class to store information about a single combat roll."""
    unit_name: str
    roll: int
    strength: int
    hit: bool
    side: str  # "Attacker" or "Defender"


class BattleRollsWindow:
    """
    Tkinter window for displaying combat roll results with visual progress bars.
    
    This window shows each unit's dice roll as a colored progress bar,
    making it easy to see which rolls succeeded and by how much.
    """
    
    def __init__(self, title: str = "Battle Rolls", dice_size: int = 6):
        """
        Initialize the battle rolls display window.
        
        Args:
            title: Window title
            dice_size: Maximum value on dice (for progress bar scaling)
        """
        self.dice_size = dice_size
        self.root = tk.Toplevel()
        self.root.title(title)
        self.root.geometry("600x400")
        
        # Configure colors
        self.colors = {
            'hit': '#4CAF50',       # Green for hits
            'miss': '#F44336',      # Red for misses
            'strength': '#2196F3',  # Blue for strength threshold
            'background': '#E0E0E0' # Light gray background
        }
        
        self._setup_ui()
        self.roll_results: List[RollResult] = []
        
    def _setup_ui(self):
        """Set up the user interface components."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title label
        title_label = ttk.Label(
            main_frame, 
            text="Combat Roll Results", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Scrollable frame for roll results
        self.canvas = tk.Canvas(main_frame, bg='white')
        self.scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Clear button
        clear_btn = ttk.Button(
            button_frame, 
            text="Clear Rolls", 
            command=self.clear_rolls
        )
        clear_btn.pack(side=tk.LEFT)
        
        # Close button
        close_btn = ttk.Button(
            button_frame, 
            text="Close", 
            command=self.root.destroy
        )
        close_btn.pack(side=tk.RIGHT)
        
        # Make window stay on top
        self.root.attributes('-topmost', True)
        
    def add_roll_result(self, unit_name: str, roll: int, strength: int, hit: bool, side: str = ""):
        """
        Add a new roll result to the display.
        
        Args:
            unit_name: Name of the unit making the roll
            roll: The dice roll result
            strength: The combat strength threshold
            hit: Whether the roll was a hit
            side: "Attacker" or "Defender"
        """
        result = RollResult(unit_name, roll, strength, hit, side)
        self.roll_results.append(result)
        self._display_roll(result)
        
        # Auto-scroll to bottom
        self.root.after(10, lambda: self.canvas.yview_moveto(1.0))
        
    def _display_roll(self, result: RollResult):
        """Display a single roll result with a visual progress bar."""
        row_frame = ttk.Frame(self.scrollable_frame)
        row_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Side indicator (colored label)
        side_color = "#FF6B6B" if result.side == "Attacker" else "#4ECDC4"
        side_label = tk.Label(
            row_frame, 
            text=result.side[:3] if result.side else "   ",
            bg=side_color,
            fg="white",
            font=("Arial", 8, "bold"),
            width=3
        )
        side_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Unit name label
        unit_label = ttk.Label(
            row_frame, 
            text=f"{result.unit_name}:",
            font=("Arial", 10),
            width=15,
            anchor="w"
        )
        unit_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Result text (pack first to reserve space)
        hit_text = "HIT" if result.hit else "MISS"
        hit_color = self.colors['hit'] if result.hit else self.colors['miss']
        result_label = tk.Label(
            row_frame,
            text=f"{result.roll}/{result.strength} - {hit_text}",
            fg=hit_color,
            font=("Arial", 10, "bold"),
            width=12,
            anchor="e"
        )
        result_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Progress bar frame (now fills remaining space)
        progress_frame = tk.Frame(row_frame, bg=self.colors['background'], height=20)
        progress_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        progress_frame.pack_propagate(False)
        
        # Create visual progress bar using Canvas
        canvas = tk.Canvas(
            progress_frame, 
            height=18, 
            bg=self.colors['background'],
            highlightthickness=0
        )
        canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=1)
        
        # Draw the progress bar after a short delay to ensure canvas is ready
        canvas.after(50, lambda: self._draw_progress_bar(canvas, result))
        
    def _draw_progress_bar(self, canvas: tk.Canvas, result: RollResult):
        """Draw a visual progress bar showing the roll result."""
        # Force canvas to update its layout
        canvas.update_idletasks()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        # If canvas still not ready, try again after a longer delay
        if width <= 1 or height <= 1:
            canvas.after(100, lambda: self._draw_progress_bar(canvas, result))
            return
            
        # Clear any existing content
        canvas.delete("all")
        
        # Calculate segment widths
        segment_width = width / self.dice_size
        
        # Draw segments
        for i in range(self.dice_size):
            x1 = i * segment_width
            x2 = (i + 1) * segment_width
            
            # Determine color for this segment
            if i < result.roll:
                if i < result.strength:
                    # This segment is part of a successful roll
                    color = self.colors['hit']
                else:
                    # This segment is part of the roll but beyond strength threshold
                    color = self.colors['miss']
            elif i < result.strength:
                # This segment is within strength threshold but not rolled
                color = self.colors['strength']
            else:
                # Empty segment
                color = self.colors['background']
                
            # Draw the segment
            canvas.create_rectangle(
                x1, 2, x2-1, height-2,
                fill=color,
                outline="white",
                width=1
            )
            
        # Draw roll indicator line
        roll_x = result.roll * segment_width
        canvas.create_line(
            roll_x, 0, roll_x, height,
            fill="black",
            width=2
        )
        
        # Draw strength indicator line
        strength_x = result.strength * segment_width
        canvas.create_line(
            strength_x, 0, strength_x, height,
            fill="blue",
            width=2,
            dash=(3, 3)
        )
        
    def clear_rolls(self):
        """Clear all displayed roll results."""
        self.roll_results.clear()
        
        # Destroy all child widgets in scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
    def show(self):
        """Show the window and bring it to front."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        
    def hide(self):
        """Hide the window."""
        self.root.withdraw()
        
    def is_visible(self) -> bool:
        """Check if the window is currently visible."""
        return self.root.winfo_viewable()


# Global instance for easy access
_battle_rolls_window: Optional[BattleRollsWindow] = None


def get_battle_rolls_window() -> BattleRollsWindow:
    """
    Get the global battle rolls window instance.
    
    Creates one if it doesn't exist.
    
    Returns:
        The global BattleRollsWindow instance
    """
    global _battle_rolls_window
    
    if _battle_rolls_window is None or not _battle_rolls_window.root.winfo_exists():
        _battle_rolls_window = BattleRollsWindow()
        
    return _battle_rolls_window


def add_roll_result(unit_name: str, roll: int, strength: int, hit: bool, side: str = ""):
    """
    Convenience function to add a roll result to the global window.
    
    Args:
        unit_name: Name of the unit making the roll
        roll: The dice roll result
        strength: The combat strength threshold
        hit: Whether the roll was a hit
        side: "Attacker" or "Defender"
    """
    window = get_battle_rolls_window()
    window.add_roll_result(unit_name, roll, strength, hit, side)
    window.show()


def clear_battle_rolls():
    """Clear all roll results from the global window."""
    if _battle_rolls_window is not None:
        _battle_rolls_window.clear_rolls()


def show_battle_rolls_window():
    """Show the battle rolls window."""
    window = get_battle_rolls_window()
    window.show()


def hide_battle_rolls_window():
    """Hide the battle rolls window."""
    if _battle_rolls_window is not None:
        _battle_rolls_window.hide()


if __name__ == "__main__":
    # Test the window
    import time
    
    root = tk.Tk()
    # root.withdraw()  # Hide main window
    
    # Create test rolls
    window = get_battle_rolls_window()
    
    # Simulate some rolls
    test_rolls = [
        ("Infantry", 3, 2, True, "Attacker"),
        ("Tank", 5, 3, False, "Attacker"),
        ("Artillery", 2, 2, True, "Attacker"),
        ("Fighter", 1, 3, True, "Defender"),
        ("Infantry", 4, 2, False, "Defender"),
        ("Submarine", 2, 2, True, "Defender"),
    ]
    
    for unit_name, roll, strength, hit, side in test_rolls:
        add_roll_result(unit_name, roll, strength, hit, side)
        time.sleep(0.5)  # Delay to see them appear one by one
        
    root.mainloop()
