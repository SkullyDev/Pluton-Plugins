__author__ = 'Skully'
__version__ = '1.0'

import clr
import sys
import math

clr.AddReferenceByPartialName("UnityEngine")
clr.AddReferenceByPartialName("Pluton")
import UnityEngine
import Pluton
import System

class AdminList:
    def On_Command(self, cmd):
        if cmd.cmd == "admins":
            for player in Server.ActivePlayers:
                if player.Admin:
                    nameList = nameList + player.Name + ", "
            if nameList == "":
                Player.Message("Sorry but there are no admins online at this moment")
            else:
                Player.Message(nameList[:-2])