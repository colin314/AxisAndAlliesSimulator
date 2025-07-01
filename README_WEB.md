# Axis & Allies Battle Simulator - Web Interface

This web application provides a modern, user-friendly interface for the Axis & Allies battle simulator. Instead of using command-line interface, you can now set up battles and view results through your web browser.

## Features

- **Interactive Web Interface**: Set up battles through a clean, modern web interface
- **Real-time Battle Simulation**: Run single battles and see immediate results
- **Statistical Analysis**: Generate statistics from multiple battle simulations
- **Visual Results**: Battle outcomes displayed with charts and statistics
- **Land and Naval Battles**: Support for both battle types
- **Power Selection**: Choose from all major powers in the game

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Option 1: Using the Batch File (Windows)
Simply double-click `start_web_app.bat` to start the server.

### Option 2: Using Python Directly
```bash
python web_app.py
```

### Option 3: Using the Virtual Environment
```bash
.venv\Scripts\python.exe web_app.py
```

## Accessing the Web App

1. After starting the server, open your web browser
2. Navigate to: `http://localhost:5000`
3. The battle simulator interface will load

## How to Use

### Setting Up a Battle

1. **Choose Battle Type**: Select either "Land Battle" or "Naval Battle"
2. **Select Powers**: Choose the attacking and defending powers from the dropdown menus
3. **Set Unit Counts**: Enter the number of each unit type for both attacker and defender
4. **Setup Battle**: Click the "Setup Battle" button to initialize the battle

### Running Simulations

- **Single Battle**: Click "Run Single Battle" to simulate one battle and see the outcome
- **Generate Statistics**: Click "Generate Statistics" to run 1000 battles and see win rates and averages
- **Reset**: Click "Reset" to clear the current setup and start over

### Understanding Results

- **Battle Results**: Shows winner, remaining units, and IPC swing for individual battles
- **Statistics**: Shows attacker win rate and average IPC swing across multiple battles
- **Unit Information**: Displays HP and cost information for both sides

## Features Explained

### Battle Types
- **Land Battle**: Uses infantry, artillery, tanks, aircraft, etc.
- **Naval Battle**: Uses ships, submarines, aircraft carriers, etc.

### Powers
Choose from: Americans, ANZAC, British, Chinese, French, Germans, Italians, Japanese, Russians, or Neutral

### Statistics
- **Win Rate**: Percentage of battles won by the attacker
- **IPC Swing**: Industrial Production Certificate value difference (economic impact)
- **HP**: Hit Points (number of units that can take hits)

## Technical Details

- Built with Flask web framework
- Uses the existing Simulator.py battle engine
- Responsive design works on desktop and mobile
- Real-time updates without page refreshes
- Captures and displays all battle output

## Files

- `web_app.py`: Main Flask application
- `templates/index.html`: Web interface template
- `requirements.txt`: Python dependencies
- `start_web_app.bat`: Windows startup script
- `README_WEB.md`: This documentation

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, you can change it in `web_app.py`:
```python
app.run(debug=True, host='localhost', port=5001)  # Change port here
```

### Dependencies Not Found
Make sure to install all requirements:
```bash
pip install flask colorama pandas tabulate Pillow
```

### Unit Images Not Loading
Ensure the `Resources` folder and unit images are in the correct location relative to the simulator files.

## Stopping the Server

- Press `Ctrl+C` in the terminal/command prompt
- Or close the terminal window
- The web interface will become unavailable until you restart the server

---

Enjoy simulating your Axis & Allies battles with the new web interface! 🎲⚔️
