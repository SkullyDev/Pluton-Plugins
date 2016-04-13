__author__ = 'Skully'
__version__ = '1.1'

import clr
import sys
import math

clr.AddReferenceByPartialName("UnityEngine")
clr.AddReferenceByPartialName("Pluton")
import UnityEngine
import Pluton


class PM:
    # OP CheckV legally stolen from DreTaX :P
    """
        CheckV Assistants
    """
    def GetPlayerName(self, name, Mode=1):
        if Mode == 1 or Mode == 3:
            for pl in Server.ActivePlayers:
                if pl.Name.lower() == name:
                    return pl
        if Mode == 2 or Mode == 3:
            for pl in Server.OfflinePlayers.Values:
                if pl.Name.lower() == name:
                    return pl
        return None

    """
        CheckV method based on Spock's method.
        Upgraded by DreTaX
        Can Handle Single argument and Array args.
        Mode: Search mode (Default: 1)
            1 = Search Online Players
            2 = Search Offline Players
            3 = Both
        V6.0
    """

    def CheckV(self, Player, args, Mode=1):
        count = 0
        if hasattr(args, '__len__') and (not isinstance(args, str)):
            p = self.GetPlayerName(str.Join(" ", args).lower(), Mode)
            if p is not None:
                return p
            if Mode == 1 or Mode == 3:
                for pl in Server.ActivePlayers:
                    for namePart in args:
                        if namePart.lower() in pl.Name.lower():
                            p = pl
                            count += 1
            if Mode == 2 or Mode == 3:
                for offlineplayer in Server.OfflinePlayers.Values:
                    for namePart in args:
                        if namePart.lower() in offlineplayer.Name.lower():
                            p = offlineplayer
                            count += 1
        else:
            ag = str(args).lower()  # just incase
            p = self.GetPlayerName(ag, Mode)
            if p is not None:
                return p
            if Mode == 1 or Mode == 3:
                for pl in Server.ActivePlayers:
                    if ag in pl.Name.lower():
                        p = pl
                        count += 1
            if Mode == 2 or Mode == 3:
                for offlineplayer in Server.OfflinePlayers.Values:
                    if ag in offlineplayer.Name.lower():
                        p = offlineplayer
                        count += 1
        if count == 0:
            Player.Message("Couldn't find " + str.Join(" ", args) + "!")
            return None
        elif count == 1 and p is not None:
            return p
        else:
            Player.Message("Found " + str(count) + " player with similar name. Use more correct name!")
            return None

    def MessageMake(self, args, name):
        message = str.Join(" ", args)
        message = message.replace(name + " ", "")
        return message

    def MessageMakeReply(self, args):
        message = str.Join(" ", args)
        return message

    def On_Command(self, cmd):
        Player = cmd.User
        args = cmd.args
        if cmd.cmd == "pm":
            if len(args) == 0:
                Player.Message("Usage: /pm PlayerName Message")
                return
            if len(args) < 2:
                Player.Message("Usage: /pm PlayerName Message")
                return
            pl = self.CheckV(Player, args[0])
            if pl is not None:
                if Player.Name is pl.Name:
                    Player.Message("You can't send PM to your self")
                    return
                message = self.MessageMake(args, args[0])
                Plugin.Log("PM_Log", "[From: " + str(Player.Name) + " To: " + str(pl.Name) + "] " + str(Player.Name) + ": " + message)
                DataStore.Add("PM", pl.SteamID, Player.SteamID)
                pl.MessageFrom("PM from " + str(Player.Name), message)
                pl.Message("To fast reply use: /r Message")
                Player.MessageFrom("PM to " + str(pl.Name), message)
        elif cmd.cmd == "r":
            if DataStore.ContainsKey("PM", Player.SteamID):
                plID = DataStore.Get("PM", Player.SteamID)
                pl = Server.FindPlayer(plID)
                message = self.MessageMakeReply(args)
                Plugin.Log("PM_Log", "[From: " + str(Player.Name) + " To: " + str(pl.Name) + "] " + str(Player.Name) + ": " + message)
                DataStore.Add("PM", plID, Player.SteamID)
                pl.MessageFrom("PM from " + str(Player.Name), message)
                pl.Message("To fast reply use: /r Message")
                Player.MessageFrom("PM to " + str(pl.Name), message)
            else:
                Player.Message("You don't have any pending pm's to reply")