__author__ = 'Skully'
__version__ = '1.7'

import clr
import sys
import math
import re

clr.AddReferenceByPartialName("UnityEngine")
clr.AddReferenceByPartialName("Pluton")
import UnityEngine
import Pluton
import System


class TPA:
    def GetPlayerName(self, names):
        name = names.lower()
        for pl in Server.ActivePlayers:
            if pl.Name.lower() == name:
                return pl
        return None

    """
        CheckV method based on Spock's method.
        Upgraded by DreTaX
        Can Handle Single argument and Array args.
        V4.0
    """
    def CheckV(self, Player, args):
        count = 0
        if hasattr(args, '__len__') and (not isinstance(args, str)):
            p = self.GetPlayerName(str.Join(" ", args))
            if p is not None:
                return p
            for pl in Server.ActivePlayers:
                for namePart in args:
                    if namePart.lower() in pl.Name.lower():
                        p = pl
                        count += 1
                        continue
        else:
            p = self.GetPlayerName(str(args))
            if p is not None:
                return p
            for pl in Server.ActivePlayers:
                if str(args).lower() in pl.Name.lower():
                    p = pl
                    count += 1
                    continue
        if count == 0:
            Player.Message("Couldn't find " + str.Join(" ", args) + "!")
            return None
        elif count == 1 and p is not None:
            return p
        else:
            Player.Message("Found " + str(count) + " player with similar name. Use more correct name!")
            return None

    def On_ServerInit(self):
        DataStore.Flush("TeleportRequest")

    def On_PlayerDisconnected(self, Player):
        if DataStore.Get("TeleportRequest", Player.SteamID):
            DataStore.Remove("TeleportRequest", Player.SteamID)

    def On_Command(self, cmd):
        if cmd.cmd == "tpa":
            if len(cmd.args) == 0:
                cmd.User.Message("USAGE: /tpa Player Name")
                return
            else:
                tpto = self.CheckV(cmd.User, cmd.args)
                if tpto is not None:
                    if tpto.Name == cmd.User.Name:
                        cmd.User.Message("You cannot teleport to your self!")
                        return
                    if DataStore.Get("TeleportRequest", tpto.SteamID) is not None:
                        cmd.User.Message("This player already has pending teleportation request...")
                        cmd.User.Message("Try again later, or tell the player to deny his current request!")
                        return
                    DataStore.Add("TeleportRequest", tpto.SteamID, cmd.User.SteamID)
                    cmd.User.Message("Teleport request sent!")
                    tpto.Message(cmd.User.Name + " wants to teleport to You! USE: /tpaccept OR /tpdeny")
                    autokill = Plugin.CreateDict()
                    autokill["PlayerR"] = cmd.User.SteamID
                    autokill["PlayerT"] = tpto.SteamID
                    Plugin.CreateParallelTimer("AutoKill", 60000, autokill).Start()
        elif cmd.cmd == "tpaccept":
            if DataStore.Get("TeleportRequest", cmd.User.SteamID):
                tphereid = DataStore.Get("TeleportRequest", cmd.User.SteamID)
                tphere = Server.FindPlayer(tphereid)
                tpherename = tphere.Name
                tpherenamestring = tpherename.ToString()
                if tphere:
                    cmd.User.Message("Teleportation request Accepted")
                    tphere.Message("Teleportation request Accepted")
                    #DreTaX code! Plugin is not for publishing, but for private use!
                    tpdelaytp = Plugin.CreateDict()
                    tpdelaytp["PlayerR"] = tphere.SteamID
                    tpdelaytp["PlayerT"] = cmd.User.SteamID
                    Plugin.CreateParallelTimer("TpDelay", 10000, tpdelaytp).Start()
                    tphere.Message("Teleporting you in 10 seconds")
                    DataStore.Remove("TeleportRequest", cmd.User.SteamID)
                else:
                    cmd.User.Message("Can't teleport, player maybe disconnected!")
                    DataStore.Remove("TeleportRequest", cmd.User.SteamID)
            else:
                cmd.User.Message("No pending requests to accept")
        elif cmd.cmd == "tpdeny":
            if DataStore.Get("TeleportRequest", cmd.User.SteamID):
                tphereid = DataStore.Get("TeleportRequest", cmd.User.SteamID)
                tphere = Server.FindPlayer(tphereid)
                if tphere:
                    cmd.User.Message("Teleportation request DENYED")
                    tphere.Message("Teleportation request DENYED")
                    DataStore.Remove("TeleportRequest", cmd.User.SteamID)
                else:
                    cmd.User.Message("Teleportation request DENYED")
                    DataStore.Remove("TeleportRequest", cmd.User.SteamID)
            else:
                cmd.User.Message("No pending requests to deny")

    #DreTaX code! Plugin is not for publishing, but for private use!
    def AutoKillCallback(self, timer):
        timer.Kill()
        autokill = timer.Args
        PlayerFrom = Server.FindPlayer(autokill["PlayerR"])
        PlayerTo = Server.FindPlayer(autokill["PlayerT"])
        if PlayerFrom is None or PlayerTo is None:
            DataStore.Remove("TeleportRequest", autokill["PlayerR"])
            return
        if not DataStore.ContainsKey("TeleportRequest", PlayerFrom.SteamID) or not DataStore.ContainsKey("TeleportRequest", PlayerTo.SteamID):
            return
        DataStore.Remove("TeleportRequest", PlayerFrom.SteamID)
        DataStore.Remove("TeleportRequest", PlayerTo.SteamID)
        PlayerFrom.Message("Teleport request timed out!")
        PlayerTo.Message("Teleport request timed out!")
        return

    #DreTaX code! Plugin is not for publishing, but for private use!
    def TpDelayCallback(self, timer):
        timer.Kill()
        tpdelaytp = timer.Args
        PlayerFrom = Server.FindPlayer(tpdelaytp["PlayerR"])
        PlayerTo = Server.FindPlayer(tpdelaytp["PlayerT"])
        if PlayerFrom is None or PlayerTo is None:
            DataStore.Remove("TeleportRequest", tpdelaytp["PlayerR"])
            DataStore.Remove("TeleportRequest", tpdelaytp["PlayerT"])
            return
        DataStore.Remove("TeleportRequest", PlayerFrom.SteamID)
        DataStore.Remove("TeleportRequest", PlayerTo.SteamID)
        PlayerFrom.Teleport(PlayerTo.X, PlayerTo.Y + 0.5, PlayerTo.Z)
        PlayerFrom.Message("You teleported to player " + str(PlayerTo.Name) + "!")
        PlayerTo.Message("Player " + str(PlayerFrom.Name) + " teleported to you!")
        return