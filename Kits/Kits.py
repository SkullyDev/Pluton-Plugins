__author__ = 'Skully'
__version__ = '1.0'

import clr

clr.AddReferenceByPartialName("Pluton")
import Pluton
import math
import System
from System import *
import re

class Kits:
    def KitsConfig(self):
        if not Plugin.IniExists("Config"):
            ini = Plugin.CreateIni("Config")
            ini.AddSetting("PlayerKits", "Default", "starter")
            ini.AddSetting("PlayerKits", "AvailableKits", "starter:1800000, vip:3600000")
            ini.Save()
        return Plugin.GetIni("Config")

    def VIPPlayers(self):
        if not Plugin.IniExists("VIPPlayers"):
            ini = Plugin.CreateIni("VIPPlayers")
            ini.AddSetting("Players", "YOUR OR VIP PLAYER ID HERE", "VIP")
            ini.Save()
        return Plugin.GetIni("VIPPlayers")

    def On_Command(self, cmd):
        Player = cmd.User
        args = cmd.args
        ini = self.KitsConfig()
        kits = ini.GetSetting("PlayerKits", "AvailableKits")
        array = kits.split(',')
        if cmd.cmd == "kit" or cmd.cmd == "kits":
            if len(args) == 0:
                Player.Message("USAGE: /kit starter")
                Player.Message("USAGE FOR VIP: /kit vip")
                return
            if not Server.LoadOuts.ContainsKey(args[0]):
                Player.Message("Kit " + str(args[0]) + " not found!")
                return
            if args[0] == "admin":
                if Player.Admin:
                    loadout = Server.LoadOuts[args[0]]
                    loadout.ToInv(Player.Inventory)
            elif args[0] == "vip":
                vip = self.VIPPlayers()
                if vip.GetSetting("Players", Player.SteamID) == "VIP":
                    get = str([s for s in array if str(args[0]) in s])
                    get = re.sub('[[\]\']+', '', get).split(':')
                    cooldown = int(get[1])
                    systick = System.Environment.TickCount
                    if DataStore.Get("startercooldown" + str(args[0]), Player.SteamID) is None:
                        DataStore.Add("startercooldown" + str(args[0]), Player.SteamID, 7)
                    time = DataStore.Get("startercooldown" + str(args[0]), Player.SteamID)
                    if (systick - time) < 0 or math.isnan(systick - time):
                        DataStore.Add("startercooldown" + str(args[0]), Player.SteamID, 7)
                        time = 7
                    calc = systick - time
                    if calc >= cooldown or time == 7:
                        loadout = Server.LoadOuts[args[0]]
                        loadout.ToInv(Player.Inventory)
                        DataStore.Add("startercooldown" + str(args[0]), Player.SteamID, System.Environment.TickCount)
                    else:
                        Player.Message("You have to wait before using this kit again!")
                        done = round((calc / 1000) / 60)
                        done2 = round((cooldown / 1000) / 60)
                        Player.Message("Remaining time left: " + str(int(done2 - done)) + " minutes")
                else:
                    Player.Message("Become one of the VIP members")
            else:
                get = str([s for s in array if str(args[0]) in s])
                get = re.sub('[[\]\']+', '', get).split(':')
                cooldown = int(get[1])
                if cooldown > 0:
                    systick = System.Environment.TickCount
                    if DataStore.Get("startercooldown" + str(args[0]), Player.SteamID) is None:
                        DataStore.Add("startercooldown" + str(args[0]), Player.SteamID, 7)
                    time = DataStore.Get("startercooldown" + str(args[0]), Player.SteamID)
                    if (systick - time) < 0 or math.isnan(systick - time):
                        DataStore.Add("startercooldown" + str(args[0]), Player.SteamID, 7)
                        time = 7
                    calc = systick - time
                    if calc >= cooldown or time == 7:
                        loadout = Server.LoadOuts[args[0]]
                        loadout.ToInv(Player.Inventory)
                        DataStore.Add("startercooldown" + str(args[0]), Player.SteamID, System.Environment.TickCount)
                    else:
                        Player.Message("You have to wait before using this kit again!")
                        done = round((calc / 1000) / 60)
                        done2 = round((cooldown / 1000) / 60)
                        Player.Message("Remaining time left: " + str(int(done2 - done)) + " minutes")
                else:
                    loadout = Server.LoadOuts[args[0]]
                    loadout.ToInv(Player.Inventory)
        elif cmd.cmd == "starter":
            ini = self.KitsConfig()
            default = ini.GetSetting("PlayerKits", "Default")
            get = str([s for s in array if str(default) in s])
            get = re.sub('[[\]\']+', '', get).split(':')
            cooldown = int(get[1])
            if cooldown > 0:
                systick = System.Environment.TickCount
                if DataStore.Get("startercooldown"+str(default), Player.SteamID) is None:
                    DataStore.Add("startercooldown"+str(default), Player.SteamID, 7)
                time = DataStore.Get("startercooldown"+str(default), Player.SteamID)
                if (systick - time) < 0 or math.isnan(systick - time):
                    DataStore.Add("startercooldown"+str(default), Player.SteamID, 7)
                    time = 7
                calc = systick - time
                if calc >= cooldown or time == 7:
                    loadout = Server.LoadOuts[default]
                    loadout.ToInv(Player.Inventory)
                    DataStore.Add("startercooldown"+str(default), Player.SteamID, System.Environment.TickCount)
                else:
                    Player.Message("You have to wait before using this again!")
                    done = round((calc / 1000) / 60)
                    done2 = round((cooldown / 1000) / 60)
                    Player.Message("Time Remaining: " + str(int(done2 - done)) + " minutes")
            else:
                loadout = Server.LoadOuts[default]
                loadout.ToInv(Player.Inventory)