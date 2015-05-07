__author__ = 'Skully'
__version__ = '2.0'

import clr
import sys
import math

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
        if DataStore.Get("TeleportRequest", Player.SteamID) is not None:
            DataStore.Remove("TeleportRequest", Player.SteamID)

    def On_Command(self, cmd):
        if cmd.cmd == "tpa" or cmd.cmd == "tpr":
            if len(cmd.args) == 0:
                cmd.User.Message("USAGE: /" + cmd.cmd + " Player Name")
                return
            PlayerFrom = cmd.User
            PlayerTo = self.CheckV(PlayerFrom, cmd.args)
            if PlayerTo is not None:
                if PlayerTo.Name == PlayerFrom.Name:
                    PlayerFrom.Message("You cannot teleport to your self")
                    return
                if DataStore.Get("TeleportRequest", PlayerTo.SteamID) is not None:
                    PlayerFrom.Message("This player already has pending teleportation request")
                    PlayerFrom.Message("Try again later, or tell the player to deny his current request")
                    return
                DataStore.Add("TeleportRequest", PlayerTo.SteamID, PlayerFrom.SteamID)
                DataStore.Add("TeleportRequest", PlayerFrom.SteamID, PlayerTo.SteamID)
                PlayerFrom.Message("Teleport request sent")
                PlayerTo.Message(PlayerFrom.Name + " wants to teleport to you")
                PlayerTo.Message("USE: /tpaccept OR /tpdeny or just wait out")
                AutoKill = Plugin.CreateDict()
                AutoKill["PlayerR"] = PlayerFrom.SteamID
                AutoKill["PlayerT"] = PlayerTo.SteamID
                Plugin.CreateParallelTimer("AutoKill", 30000, AutoKill).Start()
        elif cmd.cmd == "tpaccept":
            PlayerTo = cmd.User
            PlayerFromID = DataStore.Get("TeleportRequest", PlayerTo.SteamID)
            if PlayerFromID is None:
                PlayerTo.Message("No pending requests to accept")
                return
            PlayerFrom = Server.FindPlayer(PlayerFromID)
            if PlayerFrom is None:
                PlayerTo.Message("Can't teleport, player maybe disconnected")
                DataStore.Remove("TeleportRequest", PlayerTo.SteamID)
                return
            PlayerTo.Message("Teleportation request Accepted")
            PlayerFrom.Message("Teleportation request Accepted")
            #DreTaX code!
            TpDelay = Plugin.CreateDict()
            TpDelay["PlayerR"] = PlayerFrom.SteamID
            TpDelay["PlayerT"] = PlayerTo.SteamID
            if not DataStore.ContainsKey("VIP", PlayerFrom.SteamID):
                Plugin.CreateParallelTimer("TpDelay", 10000, TpDelay).Start()
                PlayerFrom.Message("Teleporting you in 10 seconds")
                DataStore.Remove("TeleportRequest", PlayerTo.SteamID)
                return
            Plugin.CreateParallelTimer("TpDelay", 5000, TpDelay).Start()
            PlayerFrom.Message("Teleporting you in 5 seconds")
            DataStore.Remove("TeleportRequest", PlayerTo.SteamID)
        elif cmd.cmd == "tpdeny":
            PlayerTo = cmd.User
            PlayerFromID = DataStore.Get("TeleportRequest", PlayerTo.SteamID)
            if PlayerFromID is None:
                PlayerTo.Message("No pending requests to deny")
                return
            PlayerFrom = Server.FindPlayer(PlayerFromID)
            if PlayerFrom is None:
                PlayerTo.Message("Teleportation request Denied")
                DataStore.Remove("TeleportRequest", PlayerTo.SteamID)
                return
            PlayerTo.Message("Teleportation request Denied")
            PlayerFrom.Message("Teleportation request Denied")
            DataStore.Remove("TeleportRequest", PlayerTo.SteamID)

    #DreTaX code!
    def AutoKillCallback(self, timer):
        timer.Kill()
        AutoKill = timer.Args
        PlayerFrom = Server.FindPlayer(AutoKill["PlayerR"])
        PlayerTo = Server.FindPlayer(AutoKill["PlayerT"])
        if PlayerFrom is None or PlayerTo is None:
            DataStore.Remove("TeleportRequest", AutoKill["PlayerR"])
            DataStore.Remove("TeleportRequest", AutoKill["PlayerT"])
            return
        if not DataStore.ContainsKey("TeleportRequest", PlayerFrom.SteamID) or not DataStore.ContainsKey("TeleportRequest", PlayerTo.SteamID):
            DataStore.Remove("TeleportRequest", PlayerFrom.SteamID)
            DataStore.Remove("TeleportRequest", PlayerTo.SteamID)
            return
        DataStore.Remove("TeleportRequest", PlayerFrom.SteamID)
        DataStore.Remove("TeleportRequest", PlayerTo.SteamID)
        PlayerFrom.Message("Teleport request timed out!")
        PlayerTo.Message("Teleport request timed out!")
        return

    #DreTaX code!
    def TpDelayCallback(self, timer):
        timer.Kill()
        TpDelay = timer.Args
        PlayerFrom = Server.FindPlayer(TpDelay["PlayerR"])
        PlayerTo = Server.FindPlayer(TpDelay["PlayerT"])
        if PlayerFrom is None or PlayerTo is None:
            DataStore.Remove("TeleportRequest", TpDelay["PlayerR"])
            DataStore.Remove("TeleportRequest", TpDelay["PlayerT"])
            return
        DataStore.Remove("TeleportRequest", PlayerFrom.SteamID)
        DataStore.Remove("TeleportRequest", PlayerTo.SteamID)
        PlayerFrom.Teleport(PlayerTo.X, PlayerTo.Y, PlayerTo.Z)
        PlayerFrom.Message("You teleported to player " + PlayerTo.Name)
        PlayerTo.Message("Player " + PlayerFrom.Name + " teleported to you")
        return
"""
    def On_PlayerHurt(self, PlayerHurtEvent):
        if DataStore.ContainsKey("TeleportRequest", PlayerHurtEvent.Victim.SteamID):
            TPAFriendID = DataStore.Get("TeleportRequest", PlayerHurtEvent.Victim.SteamID)
            TPAFriend = Server.FindPlayer(TPAFriendID)
            DataStore.Remove("TeleportRequest", PlayerHurtEvent.Victim.SteamID)
            DataStore.Remove("TeleportRequest", TPAFriendID)
            Plugin.GetParallelTimer("")
            PlayerHurtEvent.Victim.Message("You were hurt and teleportation was cancelled")
            TPAFriend.Message("Your friend was hurt and teleportation was cancelled")
"""