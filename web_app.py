"""
Web Application for Axis & Allies Battle Simulator

This module provides a Flask web interface for the Axis & Allies battle simulator,
allowing users to set up battles and view results through a web browser instead
of the command line.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any
import threading
import time

from Simulator import Simulator
from UI_UnitSelector import GetUnitList, Combatant
from UnitsEnum import Units

app = Flask(__name__)

# Global variables to store simulation state
current_simulator = None
battle_log = []
simulation_running = False

# Unit types for the web interface
LAND_UNITS = [
    'infantry', 'mech_infantry', 'artillery', 'armour', 
    'fighter', 'tactical_bomber', 'bomber', 'aaGun', 'conscript'
]

NAVAL_UNITS = [
    'submarine', 'destroyer', 'cruiser', 'battleship', 'carrier',
    'fighter', 'tactical_bomber', 'bomber', 'transport'
]

POWERS = [
    'Americans', 'ANZAC', 'British', 'Chinese', 'French',
    'Germans', 'Italians', 'Japanese', 'Russians', 'Neutral'
]


class WebOutput:
    """Capture output for web display instead of console."""
    
    def __init__(self):
        self.output = []
    
    def write(self, text):
        if text.strip():
            self.output.append(text.strip())
    
    def flush(self):
        pass
    
    def get_output(self):
        return self.output
    
    def clear(self):
        self.output = []


@app.route('/')
def index():
    """Main page for setting up battles."""
    return render_template('index.html', 
                         land_units=LAND_UNITS, 
                         naval_units=NAVAL_UNITS,
                         powers=POWERS)


@app.route('/setup_battle', methods=['POST'])
def setup_battle():
    """Set up a new battle with the provided units."""
    global current_simulator, battle_log
    
    try:
        data = request.json
        is_land = data.get('is_land', True)
        
        # Create combatants
        attacker_units = data.get('attacker_units', {})
        defender_units = data.get('defender_units', {})
        attacker_power = data.get('attacker_power', 'Americans')
        defender_power = data.get('defender_power', 'Germans')
        
        # Filter out units with 0 count
        attacker_units = {k: v for k, v in attacker_units.items() if v > 0}
        defender_units = {k: v for k, v in defender_units.items() if v > 0}
        
        if not attacker_units or not defender_units:
            return jsonify({'success': False, 'error': 'Both sides must have at least one unit'})
        
        # Create combatant objects
        attacker = Combatant(attacker_power, attacker_units)
        defender = Combatant(defender_power, defender_units)
        
        # Create simulator
        current_simulator = Simulator()
        current_simulator.attacker = Simulator.load_unit_collection_from_ui(attacker, "Basic")
        current_simulator.defender = Simulator.load_unit_collection_from_ui(defender, "Basic")
        
        battle_log = []
        
        return jsonify({
            'success': True,
            'attacker_hp': current_simulator.attacker.currHP(),
            'defender_hp': current_simulator.defender.currHP(),
            'attacker_cost': current_simulator.attacker.currCost(),
            'defender_cost': current_simulator.defender.currCost()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/simulate_battle', methods=['POST'])
def simulate_battle():
    """Run a single battle simulation."""
    global current_simulator, battle_log
    
    if not current_simulator:
        return jsonify({'success': False, 'error': 'No battle set up'})
    
    try:
        data = request.json
        is_land = data.get('is_land', True)
        
        # Capture output
        output_capture = WebOutput()
        
        # Redirect stdout to capture prints
        with redirect_stdout(output_capture):
            attacker_hp, defender_hp = current_simulator.simulate_battle_web(
                is_land=is_land
            )
        
        # Determine winner
        if defender_hp == 0 and attacker_hp > 0:
            winner = "Attacker"
        elif attacker_hp == 0 and defender_hp > 0:
            winner = "Defender"
        else:
            winner = "Draw"
        
        # Calculate IPC swing
        ipc_swing = current_simulator.attacker.valueDelta() - current_simulator.defender.valueDelta()
        
        result = {
            'success': True,
            'winner': winner,
            'attacker_hp': attacker_hp,
            'defender_hp': defender_hp,
            'ipc_swing': ipc_swing,
            'attacker_cost_remaining': current_simulator.attacker.currCost(),
            'defender_cost_remaining': current_simulator.defender.currCost(),
            'output': output_capture.get_output()
        }
        
        battle_log.append(result)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/generate_statistics', methods=['POST'])
def generate_statistics():
    """Generate battle statistics from multiple simulations."""
    global current_simulator
    
    if not current_simulator:
        return jsonify({'success': False, 'error': 'No battle set up'})
    
    try:
        data = request.json
        battle_count = data.get('battle_count', 1000)
        is_land = data.get('is_land', True)
        
        # Reset for statistics
        current_simulator.reset()
        
        # Run multiple simulations
        results = []
        attacker_wins = 0
        ipc_swings = []
        
        for i in range(battle_count):
            attacker_hp, defender_hp = current_simulator.simulate_battle_web(is_land=is_land)
            
            if attacker_hp > defender_hp:
                attacker_wins += 1
            
            ipc_swing = current_simulator.attacker.valueDelta() - current_simulator.defender.valueDelta()
            ipc_swings.append(ipc_swing)
            
            results.append({
                'attacker_hp': attacker_hp,
                'defender_hp': defender_hp,
                'ipc_swing': ipc_swing
            })
            
            current_simulator.reset()
        
        win_rate = (attacker_wins / battle_count) * 100
        avg_ipc_swing = sum(ipc_swings) / len(ipc_swings)
        
        return jsonify({
            'success': True,
            'battle_count': battle_count,
            'attacker_win_rate': round(win_rate, 2),
            'average_ipc_swing': round(avg_ipc_swing, 2),
            'results': results[-10:]  # Return last 10 results for display
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/get_battle_log')
def get_battle_log():
    """Get the current battle log."""
    return jsonify({'battles': battle_log})


@app.route('/reset_battle', methods=['POST'])
def reset_battle():
    """Reset the current battle."""
    global current_simulator, battle_log
    
    if current_simulator:
        current_simulator.reset()
    battle_log = []
    
    return jsonify({'success': True})


if __name__ == '__main__':
    print("Starting Axis & Allies Battle Simulator Web App...")
    print("Open your browser to: http://localhost:5000")
    app.run(debug=True, host='localhost', port=5000)
