__author__ = 'Skully'
__version__ = '2.1'

import clr
import sys

clr.AddReferenceByPartialName("UnityEngine")
clr.AddReferenceByPartialName("Pluton")
import UnityEngine
import Pluton
from UnityEngine import Vector3
import math
import System
from System import *
import re


class HomeSystem:
    def HomeIni(self):
        if not Plugin.IniExists("HomeSystem"):
            Plugin.CreateIni("HomeSystem")
        return Plugin.GetIni("HomeSystem")

    # method by Illuminati
    def CheckV(self, Player, args):
        systemname = "Rust Latvia"
        p = Server.FindPlayer(args)
        if p is not None:
            return p
        count = 0
        for pl in Server.ActivePlayers:
            for namePart in args:
                if namePart in pl.Name:
                    p = pl
                    count += 1
                    continue
        if count == 0:
            Player.MessageFrom(systemname, String.Format("Couldn't find {0}!", String.Join(" ", args)))
            return None
        elif count == 1 and p is not None:
            return p
        else:
            Player.MessageFrom(systemname, String.Format("Found {0} player with similar name. Use more correct name!"))
            return None

    def On_Command(self, cmd):
        if cmd.cmd == "home":
            if len(cmd.args) == 0:
                cmd.User.Message("USAGE: /home here OR /home go")
                return
            else:
                if "here" == cmd.quotedArgs[0]:
                    ini = self.HomeIni()
                    if ini.GetSetting("HomePositions", cmd.User.SteamID):
                        ini.DeleteSetting("HomePositions", cmd.User.SteamID)
                        ini.Save()
                    ini.AddSetting("HomePositions", cmd.User.SteamID, Vector3.ToString(cmd.User.Location))
                    ini.Save()
                    cmd.User.Message("Successfully set up home position!")
                elif "go" == cmd.quotedArgs[0]:
                    ini = self.HomeIni()
                    if ini.GetSetting("HomePositions", cmd.User.SteamID):
                        coords = ini.GetSetting("HomePositions", cmd.User.SteamID)
                        coords = coords.replace("(", "")
                        coords = coords.replace(")", "")
                        coords = coords.split(",")
                        #DreTaX code!
                        HomeSystem = Plugin.CreateDict()
                        HomeSystem["Player"] = cmd.User.SteamID
                        HomeSystem["HomeLocation"] = coords
                        Plugin.CreateParallelTimer("HomeDelay", 10000, HomeSystem).Start()
                        cmd.User.Message("Teleporting you to your home in 10 seconds")
                    else:
                        cmd.User.Message("You don't have set up home position!")
                        cmd.User.Message("Use \"/home here\" to set home position!")
                elif "admin" == cmd.quotedArgs[0]:
                    if not cmd.User.Admin:
                        cmd.User.Message("You aren't an admin!")
                        return
                    pl = self.CheckV(cmd.User, cmd.quotedArgs[1])
                    if pl is not None:
                        ini = self.HomeIni()
                        if ini.GetSetting("HomePositions", cmd.User.SteamID):
                            ini.DeleteSetting("HomePositions", cmd.User.SteamID)
                            ini.Save()
                        ini.AddSetting("HomePositions", cmd.User.SteamID, Vector3.ToString(pl.Location))
                        ini.Save()
                        cmd.User.Message("Successfully set home position!")
                else:
                    cmd.User.Message("USAGE: /home here OR /home go")

    #DreTaX code!
    def HomeDelayCallback(self, timer):
        timer.Kill()
        HomeSystem = timer.Args
        Player = Server.FindPlayer(HomeSystem["Player"])
        if Player is None:
            return
        HLoc = HomeSystem["HomeLocation"]
        HLoc = re.sub('[)\(\[\'\]]', '', str(HLoc))
        HLoc = HLoc.split(',')
        Player.Teleport(float(HLoc[0]), float(HLoc[1]) + 0.5, float(HLoc[2]))
        return