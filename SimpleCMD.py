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

class SimpleCMD:
    def SimpleCmdConfig(self):
        if not Plugin.IniExists("SimpleCmdConfig"):
            ini = Plugin.CreateIni("SimpleCmdConfig")
            ini.AddSetting("Config", "MessageFromName", "AdminCMDs")
            ini.AddSetting("Config", "ShowKickedBy", "1")
            ini.AddSetting("Config", "ShowMutedBy", "1")
            ini.AddSetting("Config", "ShowUnmutedBy", "1")
            ini.AddSetting("Config", "ShowKilledBy", "1")
            ini.AddSetting("Config", "UnmuteAllOnServerStart", "1")
            ini.AddSetting("Config", "DefaultUnmuteMessage", "You can now use chat")
            ini.AddSetting("Config", "MuteMessageWhenChating", "You are muted")
            ini.Save()
        return Plugin.GetIni("SimpleCmdConfig")

    def On_ServerInit(self):
        ini = self.SimpleCmdConfig()
        if ini.GetSetting("Config", "UnmuteAllOnServerStart") == "1":
            DataStore.Flush("mute")

    # method by Illuminati
    def CheckV(self, Player, args):
        ini = self.SimpleCmdConfig()
        systemname = ini.GetSetting("Config", "MessageFromName")
        p = Server.FindPlayer(str.Join(" ", args))
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
            Player.MessageFrom(systemname, String.Format("Found {0} player with similar name. Use more correct name!"), str(count))
            return None

    # method by Illuminati (Remake Skully)
    def CheckVv2(self, Player, args):
        ini = self.SimpleCmdConfig()
        systemname = ini.GetSetting("Config", "MessageFromName")
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
            Player.MessageFrom(systemname, "Couldn't find " + args + "!")
            return None
        elif count == 1 and p is not None:
            return p
        else:
            Player.MessageFrom(systemname, "Found " + str(count) + " player with similar name. Use more correct name!")
            return None

    def MessageMake(self, args, name):
        message = str.Join(" ", args)
        message = message.replace(name + " ", "")
        return message

    def On_Chat(self, msg):
        Player = msg.User
        if DataStore.Get("mute", Player.SteamID) is True:
            msg.BroadcastName = None
            msg.FinalText = None
            ini = self.SimpleCmdConfig()
            sysname = ini.GetSetting("Config", "MessageFromName")
            message = ini.GetSetting("Config", "MuteMessageWhenChating")
            Player.MessageFrom(sysname, message)
            return

    def On_Command(self, cmd):
        Player = cmd.User
        args = cmd.args
        if cmd.cmd == "kick":
            ini = self.SimpleCmdConfig()
            sysname = ini.GetSetting("Config", "MessageFromName")
            if Player.Admin:
                if len(args) == 0:
                    Player.MessageFrom(sysname, "Usage: /kick Name")
                    Player.MessageFrom(sysname, "Usage: /kick Name Reason")
                    return
                elif len(args) == 1:
                    pl = self.CheckV(Player, args)
                    if pl is not None:
                        if pl.Name is Player.Name:
                            Player.MessageFrom(sysname, "You cannot kick your self!")
                            return
                        if ini.GetSetting("Config", "ShowKickedBy") == "1":
                            pl.Kick("Kicked by " + Player.Name)
                        else:
                            pl.Kick("Kicked by Admin")
                        Player.MessageFrom(sysname, "Player " + pl.Name + " was kicked from server")
                else:
                    pl = self.CheckVv2(Player, args[0])
                    if pl is not None:
                        if pl.Name is Player.Name:
                            Player.MessageFrom(sysname, "You cannot kick your self!")
                            return
                        message = self.MessageMake(args, args[0])
                        if ini.GetSetting("Config", "ShowKickedBy") != "1":
                            pl.Kick("Kicked by " + Player.Name + "! Reason: " + message)
                        else:
                            pl.Kick("Kicked by Admin! Reason: " + message)
                        Player.MessageFrom(sysname, "Player " + pl.Name + " was kicked from server")
            else:
                Player.MessageFrom(sysname, "You aren't an admin!")

        elif cmd.cmd == "mute":
            ini = self.SimpleCmdConfig()
            sysname = ini.GetSetting("Config", "MessageFromName")
            if Player.Admin:
                if len(args) == 0:
                    Player.MessageFrom(sysname, "Usage: /mute Name")
                    Player.MessageFrom(sysname, "Usage: /mute Name Reason")
                    return
                elif len(args) == 1:
                    pl = self.CheckV(Player, args)
                    if pl is not None:
                        if pl.Name is Player.Name:
                            Player.MessageFrom(sysname, "You cannot mute your self!")
                            return
                        if DataStore.Get("mute", pl.SteamID) is None or DataStore.Get("mute", pl.SteamID) is False:
                            if ini.GetSetting("Config", "ShowMutedBy") == "1":
                                pl.MessageFrom(sysname, "Muted by " + Player.Name)
                            else:
                                pl.MessageFrom(sysname, "Muted by Admin!")
                            DataStore.Add("mute", pl.SteamID, True)
                            Player.MessageFrom(sysname, "Player " + pl.Name + " was muted")
                        else:
                            Player.MessageFrom(sysname, "Player " + pl.Name + " is already muted")
                else:
                    pl = self.CheckVv2(Player, args[0])
                    if pl is not None:
                        if pl.Name is Player.Name:
                            Player.MessageFrom(sysname, "You cannot mute your self!")
                            return
                        if DataStore.Get("mute", pl.SteamID) is None or DataStore.Get("mute", pl.SteamID) is False:
                            message = self.MessageMake(args, args[0])
                            if ini.GetSetting("Config", "ShowMutedBy") != "1":
                                pl.MessageFrom(sysname, "Muted by " + Player.Name + "! Reason: " + message)
                            else:
                                pl.MessageFrom(sysname, "Muted by Admin! Reason: " + message)
                            DataStore.Add("mute", pl.SteamID, True)
                            Player.MessageFrom(sysname, "Player " + pl.Name + " was muted")
                        else:
                            Player.MessageFrom(sysname, "Player " + pl.Name + " is already muted")
            else:
                Player.MessageFrom(sysname, "You aren't an admin!")

        elif cmd.cmd == "unmute":
            ini = self.SimpleCmdConfig()
            sysname = ini.GetSetting("Config", "MessageFromName")
            if Player.Admin:
                if len(args) == 0:
                    Player.MessageFrom(sysname, "Usage: /unmute Name")
                    return
                else:
                    pl = self.CheckV(Player, args)
                    if pl is not None:
                        if DataStore.Get("mute", pl.SteamID) is not None and DataStore.Get("mute", pl.SteamID) is True:
                            message = ini.GetSetting("Config", "DefaultUnmuteMessage")
                            if ini.GetSetting("Config", "ShowUnmutedBy") != "1":
                                pl.MessageFrom(sysname, "Unmuted by " + Player.Name + "! " + message)
                            else:
                                pl.MessageFrom(sysname, "Unmuted by Admin! " + message)
                            DataStore.Add("mute", pl.SteamID, False)
                            Player.MessageFrom(sysname, "Player " + pl.Name + " was unmuted")
                        else:
                            Player.MessageFrom(sysname, "Player " + pl.Name + " is already unmuted")
            else:
                Player.MessageFrom(sysname, "You aren't an admin!")

        elif cmd.cmd == "kill":
            ini = self.SimpleCmdConfig()
            sysname = ini.GetSetting("Config", "MessageFromName")
            if Player.Admin:
                if len(args) == 0:
                    Player.MessageFrom(sysname, "Usage: /kill Name")
                    Player.MessageFrom(sysname, "Usage: /kill Name Reason")
                    return
                elif len(args) == 1:
                    pl = self.CheckV(Player, args)
                    if pl is not None:
                        if pl.Name is Player.Name:
                            Player.MessageFrom(sysname, "You cannot kill your self!")
                            return
                        if ini.GetSetting("Config", "ShowKilledBy") == "1":
                            pl.Kill()
                            pl.MessageFrom(sysname, "Killed by " + Player.Name)
                        else:
                            pl.Kill()
                            pl.MessageFrom(sysname, "Killed by Admin")
                        Player.MessageFrom(sysname, "Player " + pl.Name + " was killed")
                else:
                    pl = self.CheckVv2(Player, args[0])
                    if pl is not None:
                        if pl.Name is Player.Name:
                            Player.MessageFrom(sysname, "You cannot kill your self!")
                            return
                        message = self.MessageMake(args, args[0])
                        if ini.GetSetting("Config", "ShowKilledBy") != "1":
                            pl.Kill()
                            pl.MessageFrom(sysname, "Killed by " + Player.Name + "! Reason: " + message)
                        else:
                            pl.Kill()
                            pl.MessageFrom(sysname, "Killed by Admin! Reason: " + message)
                        Player.MessageFrom(sysname, "Player " + pl.Name + " was killed")
            else:
                Player.MessageFrom(sysname, "You aren't an admin!")