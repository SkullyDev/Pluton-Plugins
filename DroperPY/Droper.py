__author__ = 'Skully'
__version__ = '2.5'

import clr
import sys
import math

clr.AddReferenceByPartialName("UnityEngine")
clr.AddReferenceByPartialName("Pluton")
import UnityEngine
import Pluton

class Droper:
    def DroperIniSettings(self):
        if not Plugin.IniExists("DroperSettings"):
            ini = Plugin.CreateIni("DroperSettings")
            ini.AddSetting("Settings", "Enabled", "1")
            ini.AddSetting("Settings", "EventEveryMins", "30")
            ini.AddSetting("Settings", "PlayersNeeded", "5")
            ini.AddSetting("Settings", "PlanesInSameTime", "1")
            ini.AddSetting("Settings", "BroadcastMsgName", "AIRDROP")
            ini.AddSetting("Settings", "BroadcastMsgLowPlayers", "AIRDROP WAS CANCELLED, NEED MORE PLAYER")
            ini.AddSetting("Settings", "BroadcastMsgAirdropIncoming", "AIRDROP CARGO PLANE INCOMING")
            ini.Save()
        return Plugin.GetIni("DroperSettings")

    def On_PluginInit(self):
        ini = self.DroperIniSettings()
        if ini.GetSetting("Settings", "Enabled") == "1":
            mins = ini.GetSetting("Settings", "EventEveryMins")
            timer = int(mins)*60000
            Plugin.CreateTimer("delayedDrop", timer).Start()

    def delayedDropCallback(self, timer):
        ini = self.DroperIniSettings()
        Online = Server.Players.Count
        Needed = ini.GetSetting("Settings", "PlayersNeeded")
        SysName = ini.GetSetting("Settings", "BroadcastMsgName")
        if Online >= int(Needed):
            i = 0
            RepeatPlanes = int(ini.GetSetting("Settings", "PlanesInSameTime"))
            while i < RepeatPlanes:
                Server.SendCommand("event.run", True)
                i = i + 1
            message = ini.GetSetting("Settings", "BroadcastMsgAirdropIncoming")
            Server.BroadcastFrom(SysName, message)
        else:
            message = ini.GetSetting("Settings", "BroadcastMsgLowPlayers")
            Server.BroadcastFrom(SysName, message)