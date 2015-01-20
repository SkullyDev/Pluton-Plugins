__author__ = 'Skully'
__version__ = '1.0'

import clr
import sys

clr.AddReferenceByPartialName("UnityEngine")
clr.AddReferenceByPartialName("Pluton")
import UnityEngine
import Pluton
import System

class GodMode:
    def On_Command(self, cmd):
        Player = cmd.User
        if cmd.cmd == "helpgod":
            if not Player.Admin:
                Player.Message("You aren't an admin!")
                return
            if DataStore.Get("godhelp", Player.SteamID) == 1:
                DataStore.Remove("godhelp", Player.SteamID)
                Player.Message("God mode turned off")
            else:
                DataStore.Add("godhelp", Player.SteamID, 1)
                Player.Health = 100
                Player.Message("God mode turned on")

    def On_PlayerHurt(self, PlayerHurtEvent):
        if DataStore.Get("godhelp", Pluton.Player.Find(PlayerHurtEvent.Victim.Name).SteamID) == 1:
            for dmg in range(0, len(PlayerHurtEvent.DamageAmounts)):
                PlayerHurtEvent.DamageAmounts[dmg] = float(0)