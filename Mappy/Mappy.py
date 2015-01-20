__author__ = 'Skully'
__version__ = '1.0'

import clr
import sys
import math
import re

clr.AddReferenceByPartialName("UnityEngine")
clr.AddReferenceByPartialName("Pluton")
import UnityEngine
import Pluton
import System

class Mappy:
    def ConfigurationFile(self):
        if not Plugin.IniExists("ConfigurationFile"):
            ini = Plugin.CreateIni("ConfigurationFile")
            ini.AddSetting("Settings", "enabled", "1")
            ini.AddSetting("Settings", "Timer", "60000")
            ini.AddSetting("Settings", "url", "http://www.example.com/mappy/server.php")
            ini.Save()
        return Plugin.GetIni("ConfigurationFile")

    def On_PluginInit(self):
        DataStore.Flush("Mappy")
        ini = self.ConfigurationFile()
        if ini.GetSetting("Settings", "enabled") == "1":
            link = ini.GetSetting("Settings", "url")
            DataStore.Add("Mappy", "Link", link)
            mseconds = ini.GetSetting("Settings", "Timer")
            msec = int(mseconds)
            Plugin.CreateTimer("Send", msec).Start()

    def SendCallback(self, timer):
        ServersTime = str(World.Time)
        post = "&time=" + ServersTime + "&players=::"
        i = 1
        for player in Server.ActivePlayers:
            if player.Location:
                Name = self.FormatName(player.Name)
                if len(Name) < 3:
                    Name = "Player - " + str(i)
                    i = i+1
                coords = str(player.Location)
                stripit = str.strip(coords, "()")
                sripped = str.strip(stripit, ",")
                splitted = sripped.split(" ")
                coordx = splitted[0]
                coordz = splitted[2]
                post = post + ";" + Name + ":" + coordx + ":" + coordz
        link = DataStore.Get("Mappy", "Link")
        Plugin.POST(link, post)

    def FormatName(self, Name):
        Name = re.sub('[\/\%\:\;\?\=\+\&]+', '', Name)
        return str(Name)