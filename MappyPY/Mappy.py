__author__ = 'Skully'
__version__ = '3.0'

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
        if args[0] == "":
            return
        if args[0] == "airdrop":
            x = args[1]
            z = args[2]
            World.AirDropAt(float(x), 0, float(z))
        elif args[0] == "kick":
            steamid = int(args[1])
            player = Pluton.Players[steamid]
            player.Kick("Mappy control panel kick")
        elif args[0] == "message":
            steamid = int(args[1])
            player = Pluton.Players[steamid]
            message = str.Join(" ", args)
            message = message.replace(args[0] + " " + args[1] + " ", "")
            player.Message(message)
        elif args[0] == "teleport":
            x = args[2]
            z = args[3]
            steamid = int(args[1])
            player = Pluton.Players[steamid]
            player.Teleport(float(x), World.GetGround(float(x), float(z)), float(z))
        elif args[0] == "give":
            steamid = int(args[1])
            player = Pluton.Players[steamid]
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
            message = str.Join(" ", args)
            message = message.replace(args[0] + " ", "")
            Server.Broadcast(message)

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
        for player in Server.ActivePlayers:
            if player.Location:
                Name = Uri.EscapeDataString(player.Name)
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
            Message = Uri.EscapeDataString(Chat.OriginalText)
            Sender = Uri.EscapeDataString(Chat.User.Name)
            link = DataStore.Get("Mappy", "LinkChat")
            post = "&chat=" + Sender + ": " + Message
            Plugin.POST(link, post)
