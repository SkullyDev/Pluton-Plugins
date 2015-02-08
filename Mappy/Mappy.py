__author__ = 'Skully'
__version__ = '2.0'

import clr
import sys
import math

clr.AddReferenceByPartialName("UnityEngine")
clr.AddReferenceByPartialName("Pluton")
clr.AddReference("Assembly-CSharp")
import World as globalWorld
import UnityEngine
import Pluton
import System
from System import Uri

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
            ServerConsoleCommands.Register("mappy").setCallback("ReceiveCommand")
            link = ini.GetSetting("Settings", "url")
            if ini.GetSetting("Settings", "SendChat") == "1":
                DataStore.Add("Mappy", "SendChat", 1)
                DataStore.Add("Mappy", "LinkChat", link + "chat.php")
            DataStore.Add("Mappy", "Link", link + "server.php")
            DataStore.Add("Mappy", "LinkSize", link + "size.php")
            mseconds = ini.GetSetting("Settings", "Timer")
            msec = int(mseconds)
            Plugin.CreateTimer("SendSizeOnce", 15000).Start()
            Plugin.CreateTimer("Send", msec).Start()

    def ReceiveCommand(self, args):
        if len(args) == 0:
            return
        if args[0] == "airdrop":
            x = args[1]
            z = args[2]
            World.AirDropAt(float(x), 0, float(z))
        elif args[0] == "kick":
            steamid = args[1]
            palyer = Pluton.Player.Find(steamid)
            player.Kick("Mappy control panel kick")
        elif args[0] == "message":
            steamid = args[1]
            palyer = Pluton.Player.Find(steamid)
            message = self.MessageMake(args)
            player.Message(message)
        elif args[0] == "teleport":
            x = args[1]
            z = args[2]
            steamid = args[3]
            palyer = Pluton.Player.Find(steamid)
            player.Teleport(float(x), World.GetGround(float(x), float(z)) + 1, float(z))
        elif args[0] == "give":
            steamid = args[1]
            palyer = Pluton.Player.Find(steamid)
            count = args[2]
            # GIVE CODE USED FROM "Give" balu92's PLUGIN
            item = Pluton.InvItem.GetItemID(args[3])
            player.Inventory.Add(item, int(count))
        elif args[0] == "animal":
            x = args[1]
            z = args[2]
            animalname = args[3]
            World.SpawnAnimal(animalname, float(x), float(z))
        elif args[0] == "broadcast":
            message = self.MessageMakeBroadcast(args)
            Server.Broadcast(message)

    def MessageMake(self, args):
        message = str.Join(" ", args)
        message = message.replace(args[0] + " " + args[1] + " ", "")
        return message

    def MessageMakeBroadcast(self, args):
        message = str.Join(" ", args)
        message = message.replace(args[0] + " ", "")
        return message

    def SendSizeOnceCallback(self, timer):
        timer.Kill()
        DataStore.Add("Mappy", "SizeSent", 1)
        link = DataStore.Get("Mappy", "LinkSize")
        WorldSize = "&worldsize=" + str(globalWorld.Size)
        Plugin.POST(link, WorldSize)

    def SendCallback(self, timer):
        ServersTime = str(World.Time)
        post = "&time=" + ServersTime + "&sleepers=" + str(Server.SleepingPlayers.Count)
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
                steamid = player.SteamID
                post = post + ";" + Name + ":" + coordx + ":" + coordz + ":" + steamid
        link = DataStore.Get("Mappy", "Link")
        Plugin.POST(link, post)

    def On_Chat(self, Chat):
        if DataStore.Get("Mappy", "SendChat") == 1:
            Message = self.FormatChatLine(Chat.OriginalText)
            Sender = self.FormatName(Chat.User.Name)
            if len(Sender) < 3:
                Sender = "Player"
            link = DataStore.Get("Mappy", "LinkChat")
            post = "&chat=" + Sender + ": " + Message
            Plugin.POST(link, post)

    def FormatName(self, Name):
        Name = Uri.EscapeDataString(Name)
        return str(Name)

    def FormatChatLine(self, Line):
        Line = Uri.EscapeDataString(Line)
        return str(Line)