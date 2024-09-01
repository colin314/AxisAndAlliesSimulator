import atlastk

BODY = """
<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title></title>
    <meta name="description" content="">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="Main.css">
</head>

<body>
    <div>
        <form>
            <p id="InfantrySection" class="UnitSection">
                <label for="infantry">Infantry:</label>
                <input type="number" name="infantry" />
            </p>
            <p id="MechInfantrySection" class="UnitSection">
                <label for="mechInfantry" class="UnitLabel">Mechanized Infantry:</label>
                <input type="number" name="mechInfantry" />
            </p>
            <p id="ArtillerySection" class="UnitSection">
                <label class="UnitLabel" for="artillery">Artillery:</label>
                <input type="number" name="artillery" />
            </p>
            <p id="TankSection" class="UnitSection">
                <label class="UnitLabel" for="tanks">Tanks:</label>
                <input type="number" name="tanks" />
            </p>
            <p id="FighterSection" class="UnitSection">
                <label class="UnitLabel" for="fighter">Fighters:</label>
                <input type="number" name="fighter" />
            </p>
            <p id="TacticalBomberSection" class="UnitSection">
                <label class="UnitLabel" for="tactBombers">Tactical Bombers:</label>
                <input type="number" name="tactBombers" />
            </p>
            <p id="StratBomberSection" class="UnitSection">
                <label class="UnitLabel" for="stratBombers">Strategic Bombers:</label>
                <input type="number" name="stratBombers" />
            </p>
        </form>
    </div>
    <script src="" async defer></script>
</body>

</html>
"""

def ac_connect(dom):
    dom.inner("",BODY)
    dom.focus("Input")

def ac_submit(dom):
    name = dom.get_value("Input")
    dom.set_value("Output", f"Hello, {name}!")
    dom.set_value("Input", "")
    dom.focus("Input")

CALLBACKS = {
    "": ac_connect,
    "Submit": ac_submit

}

atlastk.launch(CALLBACKS)