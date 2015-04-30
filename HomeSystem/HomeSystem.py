__author__ = 'Skully'
__version__ = '2.1'

import clr
import sys
import re
import math

clr.AddReferenceByPartialName("UnityEngine")
clr.AddReferenceByPartialName("Pluton")
import UnityEngine
from UnityEngine import Vector3
import Pluton
import System
from System import *

class HomeSystem:
    def HomeIni(self):
        if not Plugin.IniExists("HomeSystem"):
            Plugin.CreateIni("HomeSystem")
        return Plugin.GetIni("HomeSystem")

    def On_Command(self, cmd):
        if cmd.cmd == "home":
            if len(cmd.args) == 0:
                cmd.User.Message("USAGE: /home here OR /home go")
                return
            if "here" == cmd.args[0]:
                if not cmd.User.basePlayer.CanBuild():
                    cmd.User.Message("You cannot set home in someone's territory")
                    cmd.User.Message("You need to be authorized at tool cupboard")
                    return
                ini = self.HomeIni()
                if ini.GetSetting("HomePositions", cmd.User.SteamID) is not None:
                    ini.DeleteSetting("HomePositions", cmd.User.SteamID)
                    ini.Save()
                ini.AddSetting("HomePositions", cmd.User.SteamID, Vector3.ToString(cmd.User.Location))
                ini.Save()
                cmd.User.Message("Successfully set up home position!")
            elif "go" == cmd.args[0]:
                ini = self.HomeIni()
                if not ini.ContainsSetting("HomePositions", cmd.User.SteamID):
                    cmd.User.Message("You don't have set up home position!")
                    cmd.User.Message("Use \"/home here\" to set home position!")
                    return
                coords = ini.GetSetting("HomePositions", cmd.User.SteamID)
                coords = coords.replace("(", "")
                coords = coords.replace(")", "")
                coords = coords.split(",")
                #DreTaX code!
                HomeSystem = Plugin.CreateDict()
                HomeSystem["Player"] = cmd.User.SteamID
                HomeSystem["HomeLocation"] = coords
                if not DataStore.ContainsKey("VIP", cmd.User.SteamID):
                    Plugin.CreateParallelTimer("HomeDelay", 10000, HomeSystem).Start()
                    cmd.User.Message("Teleporting you to your home in 10 seconds")
                    DataStore.Remove("TeleportActive", cmd.User.SteamID)
                    return
                Plugin.CreateParallelTimer("HomeDelay", 5000, HomeSystem).Start()
                cmd.User.Message("Teleporting you to your home in 5 seconds")

    #DreTaX code!
    def HomeDelayCallback(self, timer):
        timer.Kill()
        HomeSystem = timer.Args
        Player = Server.FindPlayer(HomeSystem["Player"])
        if Player is None:
            DataStore.Remove("TeleportActive", HomeSystem["Player"])
            return
        HLoc = HomeSystem["HomeLocation"]
        HLoc = re.sub('[)\(\[\'\]]', '', str(HLoc))
        HLoc = HLoc.split(',')
        Player.Teleport(float(HLoc[0]), float(HLoc[1]) + 0.5, float(HLoc[2]))
        DataStore.Remove("TeleportActive", Player.SteamID)
        Player.Message("Successfully teleported home")
        return