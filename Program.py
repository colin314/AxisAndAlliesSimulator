import cmd
import sys
from Simulator import *
from colorama import init as colorama_init
from colorama import Fore
from colorama import Back
from colorama import Style


class SimProgram(cmd.Cmd):
    intro = "Welcome to the AAA battle simulator."
    prompt = "Input: "
    file = None

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.sim = Simulator()

    def do_load_a(self, arg):
        "Reload the attacker's unit collection."
        if not arg:
            arg = "Attacker Basic"
        args = str.split(arg, " ")
        if len(args) < 2:
            args.append("Basic")
        list, profile = args
        self.sim.LoadAttacker(list, profile)

    def do_load_d(self, arg):
        "Reload the attacker's unit collection."
        if not arg:
            arg = "Defender Basic"
        args = str.split(arg, " ")
        if len(args) < 2:
            args.append("Basic")
        list, profile = args
        self.sim.LoadAttacker(list, profile)

    def do_load(self, arg):
        "Reload both the attacker and defender's collections."
        if not arg:
            arg = "Attacker Defender Basic Basic"
        args = str.split(arg, " ")
        if len(args) < 2:
            args.append("Defender")
        while len(args) < 4:
            args.append("Basic")
        attacker, defender, attackerProfile, defenderProfile = args
        self.sim.LoadAttacker(attacker, attackerProfile)
        self.sim.LoadDefender(defender, defenderProfile)

    def do_simulate(self, arg):
        if not hasattr(self.sim, "attacker") or not self.sim.attacker:
            print(f"{Fore.RED}Attacker is not defined. Load the attacker before proceeding.{
                  Style.RESET_ALL}")
            return
        if not hasattr(self.sim, "defender") or not self.sim.defender:
            print(f"{Fore.RED}Defender is not defined. Load the defender before proceeding.{
                  Style.RESET_ALL}")
            return
        self.sim.simulateBattleWithStats()

    def do_q(self, arg):
        "Stop the program:  BYE"
        print("Thank you for using the AAA simulator.")
        self.close()
        return True

    # ----- record and playback -----
    def do_record(self, arg):
        "Save future commands to filename:  RECORD rose.cmd"
        self.file = open(arg, "w")

    def do_playback(self, arg):
        "Playback commands from a file:  PLAYBACK rose.cmd"
        self.close()
        with open(arg) as f:
            self.cmdqueue.extend(f.read().splitlines())

    def precmd(self, line):
        if self.file and "playback" not in line:
            print(line, file=self.file)
        return line

    def close(self):
        if self.file:
            self.file.close()
            self.file = None


if __name__ == "__main__":
    SimProgram().cmdloop()
