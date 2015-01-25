__author__ = 'Skully'
__version__ = '1.8'

import clr
import sys
import math
import re

clr.AddReferenceByPartialName("UnityEngine")
clr.AddReferenceByPartialName("Pluton")
clr.AddReference("Assembly-CSharp")
import World as globalWorld
import UnityEngine
import Pluton
import System

class Mappy:
    def ConfigurationFile(self):
        if not Plugin.IniExists("ConfigurationFile"):
            ini = Plugin.CreateIni("ConfigurationFile")
            ini.AddSetting("Settings", "enabled", "1")
            ini.AddSetting("Settings", "SendChat", "1")
            ini.AddSetting("Settings", "Timer", "60000")
            ini.AddSetting("Settings", "url", "http://www.example.com/mappy/")
            ini.Save()
        return Plugin.GetIni("ConfigurationFile")

    def On_PluginInit(self):
        DataStore.Flush("Mappy")
        ini = self.ConfigurationFile()
        if ini.GetSetting("Settings", "enabled") == "1":
            link = ini.GetSetting("Settings", "url")
            if ini.GetSetting("Settings", "SendChat") == "1":
                DataStore.Add("Mappy", "SendChat", 1)
                DataStore.Add("Mappy", "LinkChat", link + "chat.php")
            DataStore.Add("Mappy", "Link", link + "server.php")
            DataStore.Add("Mappy", "LinkSize", link + "size.php")
            mseconds = ini.GetSetting("Settings", "Timer")
            msec = int(mseconds)
            Plugin.CreateTimer("SendSizeTwice", 15000).Start()
            Plugin.CreateTimer("Send", msec).Start()

    def SendSizeTwiceCallback(self, timer):
        if DataStore.Get("Mappy", "SizeSent") == 1:
            timer.Kill()
            return
        DataStore.Add("Mappy", "SizeSent", 1)
        link = DataStore.Get("Mappy", "LinkSize")
        WorldSize = "&worldsize=" + str(globalWorld.Size)
        Plugin.POST(link, WorldSize)

    def SendCallback(self, timer):
        ServersTime = str(World.Time)
        post = "&time=" + ServersTime
        if DataStore.Get("Mappy", "SendChat") == 1:
            post = post + "&showchat=true"
        post = post + "&players=::"
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
        Name = re.sub('[^0-9a-zA-Z\-\ \,\.\*\_\(\)\?\!\@\#\$\^\"\'\<\>\\\~\`\=\|\{\}\[\]]+', '', Name)
        return str(Name)

    def FormatChatLine(self, Line):
        Line = re.sub('[^0-9a-zA-Z\-\ \,\.\*\_\(\)\?\!\@\#\$\^\"\'\<\>\\\~\`\=\|\{\}\[\]\;]+', '', Line)
        return str(Line)

    def On_Chat(self, Chat):
        if DataStore.Get("Mappy", "SendChat") == 1:
            Message = self.FormatChatLine(Chat.OriginalText)
            Sender = self.FormatName(Chat.User.Name)
            if len(Sender) < 3:
                Sender = "Player"
            link = DataStore.Get("Mappy", "LinkChat")
            post = "&chat=" + Sender + ": " + Message
            Plugin.POST(link, post)