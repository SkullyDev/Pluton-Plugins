__author__ = 'Skully'
__version__ = '0.1'

import clr
import math
import sys
import re

clr.AddReferenceByPartialName("UnityEngine")
clr.AddReferenceByPartialName("Pluton")
import UnityEngine
import Pluton
import System
from System import *

class TopList:
    def ConfigurationFile(self):
        if not Plugin.IniExists("ConfigurationFile"):
            ini = Plugin.CreateIni("ConfigurationFile")
            ini.AddSetting("Settings", "enabled", "1")
            ini.AddSetting("Settings", "SystemName", "TopList")
            ini.Save()
        return Plugin.GetIni("ConfigurationFile")

    def TopListData(self):
        if not Plugin.IniExists("TopListDataFile"):
            ini = Plugin.CreateIni("TopListDataFile")
            ini.AddSetting("", "", "")
            ini.Save()
        return Plugin.GetIni("TopListData")

    def SaveTheDataAnimal(self, timer):
        NewData = timer
        DataFile = self.PlayerData(str(NewData["ID"]))
        Animal = int(float(DataFile.GetSetting("Data", NewData["AnimalName"])))
        Animales = int(Animal) + int("1")
        DataFile.DeleteSetting("Data", NewData["AnimalName"])
        DataFile.AddSetting("Data", NewData["AnimalName"], str(Animales))
        DataFile.Save()
        AnimalKills = DataFile.GetSetting("Data", "animkills")
        AnimalesKilles = int(AnimalKills) + int("1")
        DataFile.DeleteSetting("Data", "animkills")
        DataFile.AddSetting("Data", "animkills", str(AnimalesKilles))
        DataFile.Save()
        DataFile.DeleteSetting("Data", "weapon")
        DataFile.AddSetting("Data", "weapon", NewData["Weapon"])
        DataFile.Save()
        if NewData["MaxRange"] is not None:
            MaxeRange = DataFile.GetSetting("Data", "animalmaxrange")
            if NewData["MaxRange"] > int(MaxeRange):
                DataFile.DeleteSetting("Data", "animalmaxrange")
                DataFile.AddSetting("Data", "animalmaxrange", str(NewData["MaxRange"]))
                DataFile.Save()
        return

    def SaveTheDataDeath(self, timer):
        NewData = timer
        DataFile = self.PlayerData(str(NewData["ID"]))
        Deaths = DataFile.GetSetting("Data", "deaths")
        Deaths = int(Deaths) + int("1")
        DataFile.DeleteSetting("Data", "deaths")
        DataFile.AddSetting("Data", "deaths", str(Deaths))
        DataFile.Save()
        return

    def SaveTheDataDeathSuicide(self, timer):
        NewData = timer
        DataFile = self.PlayerData(str(NewData["ID"]))
        Deaths = DataFile.GetSetting("Data", "deaths")
        Deaths = int(Deaths) + int("1")
        DataFile.DeleteSetting("Data", "deaths")
        DataFile.AddSetting("Data", "deaths", str(Deaths))
        DataFile.Save()
        Suicides = DataFile.GetSetting("Data", "suicides")
        Suicides = int(Suicides) + int("1")
        DataFile.DeleteSetting("Data", "suicides")
        DataFile.AddSetting("Data", "suicides", str(Suicides))
        DataFile.Save()
        return

    def SaveTheData(self, timer):
        NewData = timer
        DataFile = self.PlayerData(str(NewData["ID"]))
        Kills = DataFile.GetSetting("Data", "kills")
        Killes = int(Kills) + int("1")
        DataFile.DeleteSetting("Data", "kills")
        DataFile.AddSetting("Data", "kills", str(Killes))
        DataFile.Save()
        if NewData["MaxRange"] is not None:
            MaxeRange = DataFile.GetSetting("Data", "maxrange")
            if NewData["MaxRange"] > int(MaxeRange):
                DataFile.DeleteSetting("Data", "maxrange")
                DataFile.AddSetting("Data", "maxrange", str(NewData["MaxRange"]))
                DataFile.Save()
        if NewData["Headshot"] is not None:
            Headshots = DataFile.GetSetting("Data", "headshots")
            Headshotes = int(Headshot) + int("1")
            DataFile.DeleteSetting("Data", "headshots")
            DataFile.AddSetting("Data", "headshots", str(Headshotes))
            DataFile.Save()
        if NewData["Weapon"] is not None:
            DataFile.DeleteSetting("Data", "weapon")
            DataFile.AddSetting("Data", "weapon", NewData["Weapon"])
            DataFile.Save()
        return

    def On_PluginInit(self):
        ini = self.ConfigurationFile()
        if ini.GetSetting("Settings", "enabled") == "1":
            DataStore.Add("TopList", "enabled", 1)

    def On_PlayerConnected(self, player):
        if DataStore.Get("TopList", "enabled") == 1:
            if player is not None:
                self.PlayerData(player.SteamID)

    def PlayerData(self, id):
        if not (Plugin.IniExists("Data-" + str(id))):
            player = Pluton.Player.FindBySteamID(id)
            playersname = player.Name
            ini = Plugin.CreateIni("Data-" + str(id))
            ini.AddSetting("Data", "name", playersname)
            ini.AddSetting("Data", "kills", "0")
            ini.AddSetting("Data", "deaths", "0")
            ini.AddSetting("Data", "suicides", "0")
            ini.AddSetting("Data", "headshots", "0")
            ini.AddSetting("Data", "maxrange", "0")
            ini.AddSetting("Data", "weapon", "Rock")
            ini.AddSetting("Data", "bear", "0")
            ini.AddSetting("Data", "wolf", "0")
            ini.AddSetting("Data", "stag", "0")
            ini.AddSetting("Data", "boar", "0")
            ini.AddSetting("Data", "chicken", "0")
            ini.AddSetting("Data", "rabbit", "0")
            ini.AddSetting("Data", "animalmaxrange", "0")
            ini.AddSetting("Data", "animkills", "0")
            ini.Save()
        return Plugin.GetIni("Data-" + str(id))

    def IsEntity(self, Stringy):
        name = ""
        if Stringy == "autospawn/animals/bear":
            name = "bear"
        elif Stringy == "autospawn/animals/wolf":
            name = "wolf"
        elif Stringy == "items/campfire_deployed":
            name = "fire"
        elif Stringy == "items/beartrap":
            name = "beartrap"
        return name

    def On_PlayerDied(self, PlayerDeathEvent):
        if DataStore.Get("TopList", "enabled") == 1:
            if PlayerDeathEvent.Attacker.ToPlayer() is None:
                attacker = PlayerDeathEvent.Attacker
                Entity = self.IsEntity(attacker.Name)
                if Entity == "":
                    return
                victim = Pluton.Player.Find(PlayerDeathEvent.Victim.Name)
                if victim is None:
                    for p in Server.SleepingPlayers:
                        if p.Name == PlayerDeathEvent.Victim.Name:
                            victimID = str(p.SteamID)
                            victimnewdata = Plugin.CreateDict()
                            victimnewdata["ID"] = victimID
                            self.SaveTheDataDeath(victimnewdata)
                            return
                victimID = str(victim.SteamID)
                victimnewdata = Plugin.CreateDict()
                victimnewdata["ID"] = victimID
                self.SaveTheDataDeath(victimnewdata)
            else:
                if str(PlayerDeathEvent.DamageType) == "Bleeding":
                    victim = Pluton.Player.Find(PlayerDeathEvent.Victim.Name)
                    victimID = str(victim.SteamID)
                    victimnewdata = Plugin.CreateDict()
                    victimnewdata["ID"] = victimID
                    self.SaveTheDataDeath(victimnewdata)
                    return
                victim = Pluton.Player.Find(PlayerDeathEvent.Victim.Name)
                victimID = str(victim.SteamID)
                attacker = Pluton.Player.Find(PlayerDeathEvent.Attacker.Name)
                attackerID = str(attacker.SteamID)
                if attackerID == victimID:
                    victimnewdata = Plugin.CreateDict()
                    victimnewdata["ID"] = victimID
                    self.SaveTheDataDeathSuicide(victimnewdata)
                elif attackerID != victimID:
                    type = str(PlayerDeathEvent.DamageType)
                    if type == "Bullet":
                        dist = round(Util.GetVectorsDistance(victim.Location, attacker.Location), 0)
                        Server.Broadcast(str(dist) + "m")
                        weapon = str(PlayerDeathEvent.Weapon.Name)
                        headshot = None
                        if str(PlayerDeathEvent.HitBone) == "head":
                            headshot = 1
                        victimnewdata = Plugin.CreateDict()
                        victimnewdata["ID"] = victimID
                        attackernewdata = Plugin.CreateDict()
                        attackernewdata["ID"] = attackerID
                        attackernewdata["Weapon"] = weapon
                        attackernewdata["MaxRange"] = dist
                        attackernewdata["Headshot"] = headshot
                        self.SaveTheDataDeath(victimnewdata)
                        self.SaveTheData(attackernewdata)
                    elif type == "Slash":
                        dist = round(Util.GetVectorsDistance(victim.Location, attacker.transform.position), 0)
                        weapon = str(PlayerDeathEvent.Weapon.Name)
                        victimnewdata = Plugin.CreateDict()
                        victimnewdata["ID"] = victimID
                        attackernewdata = Plugin.CreateDict()
                        attackernewdata["ID"] = attackerID
                        attackernewdata["Weapon"] = weapon
                        attackernewdata["MaxRange"] = dist
                        self.SaveTheDataDeath(victimnewdata)
                        self.SaveTheData(attackernewdata)
                    else:
                        victimnewdata = Plugin.CreateDict()
                        victimnewdata["ID"] = victimID
                        self.SaveTheDataDeath(victimnewdata)

    def On_NPCKilled(self, NPCDeathEvent):
        if NPCDeathEvent.Attacker.ToPlayer() is None:
            return
        if DataStore.Get("TopList", "enabled") == 1:
            victim = NPCDeathEvent.Victim
            victimname = self.IsEntity(victim.Name)
            if victimname == "":
                return
            attacker = Pluton.Player.Find(NPCDeathEvent.Attacker.Name)
            attackerID = attacker.GameID
            attackername = attacker.Name
            weapon = NPCDeathEvent.Weapon.Name
            range = round(Util.GetVectorsDistance(victim.Location, attacker.Location), 0)
            attackernewdata = Plugin.CreateDict()
            attackernewdata["AnimalName"] = victimname
            attackernewdata["ID"] = attackerID
            attackernewdata["Weapon"] = weapon
            attackernewdata["MaxRange"] = int(range)
            self.SaveTheDataAnimal(attackernewdata)