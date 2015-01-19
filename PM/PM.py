__author__ = 'Skully'
__version__ = '1.0'

import clr
import sys
import math

clr.AddReferenceByPartialName("UnityEngine")
clr.AddReferenceByPartialName("Pluton")
import UnityEngine
import Pluton

class PM:
    # method by Illuminati (Remake Skully)
    def CheckV(self, Player, args):
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
            Player.Message("Couldn't find " + args + "!")
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
                Player.Message("Usage: /pm \"Player Name\" Message")
                return
            if len(args) < 2:
                Player.Message("Usage: /pm \"Player Name\" Message")
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