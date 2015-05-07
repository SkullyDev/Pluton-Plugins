__author__ = 'Skully'
__version__ = '1.1.0'

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

class DeathMSG:
    """
        Parts brought to you by XCorrosionX and DreTaX
    """
    BodyParts = {
        'l_upperarm': 'Upper Arm',
        'r_upperarm': 'Upper Arm',
        'head': 'Head',
        'jaw': 'Head',
        'l_knee': 'Knee',
        'r_knee': 'Knee',
        'spine1': 'Spine',
        'spine2': 'Spine',
        'spine3': 'Spine',
        'spine4': 'Spine',
        'l_hand': 'Hand',
        'r_hand': 'Hand',
        'r_hip': 'Hip',
        'l_hip': 'Hip',
        'l_eye': 'Eye',
        'r_eye': 'Eye',
        'l_toe': 'Toe',
        'r_toe': 'Toe',
        'pelvis': 'Pelvis',
        'l_clavicle': 'Clavicle',
        'r_clavicle': 'Clavicle',
        'r_forearm': 'Fore Arm',
        'l_forearm': 'Fore Arm',
        'r_ulna': 'Ulna',
        'l_ulna': 'Ulna',
        'r_foot': 'Foot',
        'l_foot': 'Foot',
        'neck': 'Neck'
    }
    
    Objects = {
        'autospawn/animals/bear': 'bear',
        'autospawn/animals/wolf': 'wolf',
        'campfire_deployed(Clone)': 'fire',
        'beartrap(Clone)': 'beartrap',
        'grenade.f1.deployed(Clone)': 'F1 grenade',
        'timed.explosive.deployed(Clone)': 'timed explosive',
        'rocket_basic(Clone)': 'rocket',
        'items/barricades/barricade.wood': 'wooden barricade',
        'items/barricades/barricade.woodwire': 'wired wooden barricade',
        'items/barricades/barricade.metal': 'metal barricade'
    }

    IsAnimal = {
        'autospawn/animals/bear': 'bear',
        'autospawn/animals/wolf': 'wolf',
        'autospawn/animals/stag': 'stag',
        'autospawn/animals/boar': 'boar',
        'autospawn/animals/horse': 'horse',
        'autospawn/animals/chicken': 'chicken'
    }

    def DeathMSGConfig(self):
        if not Plugin.IniExists("DeathMSGConfig"):
            loc = Plugin.CreateIni("DeathMSGConfig")
            loc.AddSetting("Settings", "SysName", "DEATH & KILL")
            loc.AddSetting("Settings", "NaturalDies", "1")
            loc.AddSetting("Settings", "KillLog", "1")
            loc.AddSetting("Settings", "AnimalKills", "1")
            loc.AddSetting("Settings", "SleepingKills", "1")
            loc.AddSetting("Settings", "AnimalDeaths", "1")
            loc.AddSetting("Settings", "SysNameColor", "FFAA55")
            loc.AddSetting("Settings", "MessageColor", "white")
            loc.AddSetting("Settings", "Animal", "victim was killed by a killer")
            loc.AddSetting("Settings", "Suicide", "victim committed suicide...")
            loc.AddSetting("Settings", "Bite", "victim was bitten to death")
            loc.AddSetting("Settings", "Blunt", "killer hit victim in bodypart using weapon")
            loc.AddSetting("Settings", "Heat", "victim burned to death")
            loc.AddSetting("Settings", "Poison", "victim poisoned him self to death")
            loc.AddSetting("Settings", "Bow", "killer shot victim in bodypart, from distm using weapon")
            loc.AddSetting("Settings", "Hunger", "victim starved to death")
            loc.AddSetting("Settings", "Radiation", "victim died from radiation")
            loc.AddSetting("Settings", "Thirst", "victim died from thirst")
            loc.AddSetting("Settings", "Fall", "victim fell from a high place and died")
            loc.AddSetting("Settings", "Bleeding", "victim bled out")
            loc.AddSetting("Settings", "Beartrap", "victim ran on to killer's bear trap")
            loc.AddSetting("Settings", "BeartrapOwn", "victim ran on to his own bear trap")
            loc.AddSetting("Settings", "Drowned", "victim drowned")
            loc.AddSetting("Settings", "Cold", "victim caught cold and died")
            loc.AddSetting("Settings", "Bullet", "killer shot victim in bodypart, from distm using weapon")
            loc.AddSetting("Settings", "Slash", "killer slashed victim in bodypart, from distm using weapon")
            loc.AddSetting("Settings", "BiteSleep", "victim was bitten to death while he was sleeping")
            loc.AddSetting("Settings", "BluntSleep", "killer hit victim while he was sleeping in bodypart using weapon")
            loc.AddSetting("Settings", "BleedingSleep", "victim bled out while he was sleeping")
            loc.AddSetting("Settings", "StabSleep", "killer hit victim while he was sleeping in bodypart using weapon")
            loc.AddSetting("Settings", "BowSleep", "killer shot victim while he was sleeping in bodypart, from distm using weapon")
            loc.AddSetting("Settings", "BulletSleep", "killer shot victim while he was sleeping in bodypart, from distm using weapon")
            loc.AddSetting("Settings", "SlashSleep", "killer slashed victim while he was sleeping in bodypart, from distm using weapon")
            loc.AddSetting("Settings", "ExplosionSleep", "victim was blown up by killer while he was sleeping")
            loc.AddSetting("Settings", "AnimalDeath", "killer killed animal using weapon")
            loc.AddSetting("Settings", "Explosion", "victim was blown up by killer")
            loc.AddSetting("Settings", "Slasher", "victim ran in to killer and bled out")
            loc.AddSetting("Settings", "Stabber", "victim ran in to killer and bled out")
            loc.Save()
        return Plugin.GetIni("DeathMSGConfig")

    def On_PluginInit(self):
        self.DeathMSGConfig()

    def SendTheMessage(self, sysname, msg, sysnamecolor, msgcolor):
        Server.BroadcastFrom("<color=" + sysnamecolor + ">" + sysname + "</color>", "<color=" + msgcolor + ">" + msg + "</color>")

    def On_PlayerDied(self, PlayerDeathEvent):
        Attacker = PlayerDeathEvent.Attacker
        AttackerName = Attacker.Name
        Victim = PlayerDeathEvent.Victim
        Sleeping = False
        if Victim.basePlayer.IsSleeping():
            Sleeping = True
        VictimName = Victim.Name
        type = str(PlayerDeathEvent.DamageType)
        #print(type)
        #print(Victim.Name)
        #print(Attacker.Name)
        #print(PlayerDeathEvent.Weapon.Name)
        ini = self.DeathMSGConfig()
        sysname = ini.GetSetting("Settings", "SysName")
        sysnamecolor = str(ini.GetSetting("Settings", "SysNameColor"))
        msgcolor = str(ini.GetSetting("Settings", "MessageColor"))
        KillLog = int(ini.GetSetting("Settings", "KillLog"))
        if Attacker.ToPlayer() is None:
            AttackerName = self.Objects.get(AttackerName, AttackerName)
            if AttackerName is None or AttackerName == "":
                self.SendTheMessage(sysname, VictimName + " died", sysnamecolor, msgcolor)
            elif type == "Explosion":
                if Sleeping:
                    msg = ini.GetSetting("Settings", "ExplosionSleep")
                else:
                    msg = ini.GetSetting("Settings", "Explosion")
                msg = msg.replace("victim", VictimName)
                msg = msg.replace("killer", AttackerName)
                self.SendTheMessage(sysname, msg, sysnamecolor, msgcolor)
                if KillLog == 1:
                    Plugin.Log("KillLog", str(System.DateTime.Now) + " " + msg)
            elif type == "Slash":
                msg = ini.GetSetting("Settings", "Slasher")
                msg = msg.replace("victim", VictimName)
                msg = msg.replace("killer", AttackerName)
                self.SendTheMessage(sysname, msg, sysnamecolor, msgcolor)
                if KillLog == 1:
                    Plugin.Log("KillLog", str(System.DateTime.Now) + " " + msg)
            elif type == "Stab":
                msg = ini.GetSetting("Settings", "Stabber")
                msg = msg.replace("victim", VictimName)
                msg = msg.replace("killer", AttackerName)
                self.SendTheMessage(sysname, msg, sysnamecolor, msgcolor)
                if KillLog == 1:
                    Plugin.Log("KillLog", str(System.DateTime.Now) + " " + msg)
            elif type == "Heat":
                msg = ini.GetSetting("Settings", "Heat")
                msg = msg.replace("victim", VictimName)
                self.SendTheMessage(sysname, msg, sysnamecolor, msgcolor)
                if KillLog == 1:
                    Plugin.Log("KillLog", str(System.DateTime.Now) + " " + msg)
            else:
                AnimalMSG = int(ini.GetSetting("Settings", "AnimalKills"))
                if AnimalMSG == 1:
                    if type == "Bite":
                        if Sleeping:
                            msg = ini.GetSetting("Settings", "BiteSleep")
                        else:
                            msg = ini.GetSetting("Settings", "Bite")
                        msg = msg.replace("killer", AttackerName)
                        msg = msg.replace("victim", VictimName)
                        self.SendTheMessage(sysname, msg, sysnamecolor, msgcolor)
                        if KillLog == 1:
                            Plugin.Log("KillLog", str(System.DateTime.Now) + " " + msg)
        else:
            if Victim.IsWounded:
                if type == "Bite":
                    sysname = ini.GetSetting("Settings", "SysName")
                    if Victim == Attacker:
                        msg = ini.GetSetting("Settings", "BeartrapOwn")
                    else:
                        msg = ini.GetSetting("Settings", "Beartrap")
                    msg = msg.replace("victim", Victim.Name)
                    msg = msg.replace("killer", Victim.Name)
                    self.SendTheMessage(sysname, msg, sysnamecolor, msgcolor)
                    if KillLog == 1:
                        Plugin.Log("KillLog", str(System.DateTime.Now) + " " + msg)
                elif type == "Bleeding":
                    sysname = ini.GetSetting("Settings", "SysName")
                    if Sleeping:
                        msg = ini.GetSetting("Settings", "BleedingSleep")
                    else:
                        msg = ini.GetSetting("Settings", "Bleeding")
                    msg = msg.replace("victim", Victim.Name)
                    self.SendTheMessage(sysname, msg, sysnamecolor, msgcolor)
                    if KillLog == 1:
                        Plugin.Log("KillLog", str(System.DateTime.Now) + " " + msg)
                elif type == "Bullet" or type == "Slash":
                    sysname = ini.GetSetting("Settings", "SysName")
                    if PlayerDeathEvent.Weapon is not None:
                        Weapon = PlayerDeathEvent.Weapon.Name
                    else:
                        Weapon = "some weapon"
                    if Sleeping and type == "Slash":
                        dmgmsg = ini.GetSetting("Settings", "SlashSleep")
                    elif Sleeping and type == "Bullet":
                        dmgmsg = ini.GetSetting("Settings", "BulletSleep")
                    else:
                        dmgmsg = ini.GetSetting("Settings", type)
                    bodypart = str(PlayerDeathEvent.HitBone)
                    bpart = self.BodyParts.get(bodypart, bodypart)
                    if bodypart == bpart and not bodypart == "head" and not bodypart == "neck":
                        bpart = "body"
                    vloc = Victim.Location
                    aloc = Attacker.Location
                    dist = round(Util.GetVectorsDistance(vloc, aloc), 2)
                    dmgmsg = dmgmsg.replace("killer", AttackerName)
                    dmgmsg = dmgmsg.replace("victim", VictimName)
                    dmgmsg = dmgmsg.replace("dist", str(dist))
                    if PlayerDeathEvent.Weapon is not None:
                        Weapon = PlayerDeathEvent.Weapon.Name
                    else:
                        Weapon = "some weapon"
                    dmgmsg = dmgmsg.replace("weapon", Weapon)
                    dmgmsg = dmgmsg.replace("bodypart", bpart)
                    self.SendTheMessage(sysname, dmgmsg, sysnamecolor, msgcolor)
                    if KillLog == 1:
                        Plugin.Log("KillLog", str(System.DateTime.Now) + " " + dmgmsg)
                elif type == "Blunt":
                    sysname = ini.GetSetting("Settings", "SysName")
                    if PlayerDeathEvent.Weapon is not None:
                        Weapon = PlayerDeathEvent.Weapon.Name
                    else:
                        Weapon = "some weapon"
                    if Sleeping:
                        dmgmsg = ini.GetSetting("Settings", "BluntSleep")
                    else:
                        dmgmsg = ini.GetSetting("Settings", "Blunt")
                    bodypart = str(PlayerDeathEvent.HitBone)
                    bpart = self.BodyParts.get(bodypart, bodypart)
                    if bodypart == bpart and not bodypart == "head" and not bodypart == "neck":
                        bpart = "body"
                    vloc = Victim.Location
                    aloc = Attacker.Location
                    dist = round(Util.GetVectorsDistance(vloc, aloc), 2)
                    dmgmsg = dmgmsg.replace("killer", AttackerName)
                    dmgmsg = dmgmsg.replace("victim", VictimName)
                    dmgmsg = dmgmsg.replace("weapon", Weapon)
                    dmgmsg = dmgmsg.replace("bodypart", bpart)
                    self.SendTheMessage(sysname, dmgmsg, sysnamecolor, msgcolor)
                    if KillLog == 1:
                        Plugin.Log("KillLog", str(System.DateTime.Now) + " " + dmgmsg)
                elif type == "Stab":
                    sysname = ini.GetSetting("Settings", "SysName")
                    if PlayerDeathEvent.Weapon is not None:
                        Weapon = PlayerDeathEvent.Weapon.Name
                    else:
                        Weapon = "some weapon"
                    if Weapon == "Hunting Bow":
                        if Sleeping:
                            dmgmsg = ini.GetSetting("Settings", "BowSleep")
                        else:
                            dmgmsg = ini.GetSetting("Settings", "Bow")
                    else:
                        if Sleeping:
                            dmgmsg = ini.GetSetting("Settings", "StabSleep")
                        else:
                            dmgmsg = ini.GetSetting("Settings", "Stab")
                    bodypart = str(PlayerDeathEvent.HitBone)
                    bpart = self.BodyParts.get(bodypart, bodypart)
                    if bodypart == bpart and not bodypart == "head" and not bodypart == "neck":
                        bpart = "body"
                    vloc = Victim.Location
                    aloc = Attacker.Location
                    dist = round(Util.GetVectorsDistance(vloc, aloc), 2)
                    dmgmsg = dmgmsg.replace("killer", AttackerName)
                    dmgmsg = dmgmsg.replace("victim", VictimName)
                    dmgmsg = dmgmsg.replace("dist", str(dist))
                    dmgmsg = dmgmsg.replace("weapon", Weapon)
                    dmgmsg = dmgmsg.replace("bodypart", bpart)
                    self.SendTheMessage(sysname, dmgmsg, sysnamecolor, msgcolor)
                    if KillLog == 1:
                        Plugin.Log("KillLog", str(System.DateTime.Now) + " " + dmgmsg)
                elif type == "Slash":
                    sysname = ini.GetSetting("Settings", "SysName")
                    if PlayerDeathEvent.Weapon is not None:
                        Weapon = PlayerDeathEvent.Weapon.Name
                    else:
                        Weapon = "some weapon"
                    if Sleeping:
                        dmgmsg = ini.GetSetting("Settings", "SlashSleep")
                    else:
                        dmgmsg = ini.GetSetting("Settings", "Slash")
                    bodypart = str(PlayerDeathEvent.HitBone)
                    bpart = self.BodyParts.get(bodypart, bodypart)
                    if bodypart == bpart and not bodypart == "head" and not bodypart == "neck":
                        bpart = "body"
                    vloc = Victim.Location
                    aloc = Attacker.Location
                    dist = round(Util.GetVectorsDistance(vloc, aloc), 2)
                    dmgmsg = dmgmsg.replace("killer", AttackerName)
                    dmgmsg = dmgmsg.replace("victim", VictimName)
                    dmgmsg = dmgmsg.replace("dist", str(dist))
                    dmgmsg = dmgmsg.replace("weapon", Weapon)
                    dmgmsg = dmgmsg.replace("bodypart", bpart)
                    self.SendTheMessage(sysname, dmgmsg, sysnamecolor, msgcolor)
                    if KillLog == 1:
                        Plugin.Log("KillLog", str(System.DateTime.Now) + " " + dmgmsg)
                else:
                    NaturalDies = int(ini.GetSetting("Settings", "NaturalDies"))
                    if NaturalDies == 1:
                        sysname = ini.GetSetting("Settings", "SysName")
                        msg = ini.GetSetting("Settings", type)
                        msg = msg.replace("victim", VictimName)
                        self.SendTheMessage(sysname, msg, sysnamecolor, msgcolor)
                        if KillLog == 1:
                            Plugin.Log("KillLog", str(System.DateTime.Now) + " " + msg)

    def On_NPCKilled(self, NPCDeathEvent):
        if NPCDeathEvent.Attacker.ToPlayer() is None:
            return
        #print(str(NPCDeathEvent.DamageType))
        #print(NPCDeathEvent.Victim.Name)
        #print(NPCDeathEvent.Attacker.ToPlayer().Name)
        #print(NPCDeathEvent.Weapon.Name)
        ini = self.DeathMSGConfig()
        AnimalKills = int(ini.GetSetting("Settings", "AnimalDeaths"))
        if AnimalKills == 1:
            Victim = NPCDeathEvent.Victim
            Attacker = NPCDeathEvent.Attacker.ToPlayer()
            VictimName = self.IsAnimal.get(Victim.Name, Victim.Name)
            AttackerName = Attacker.Name
            if NPCDeathEvent.Weapon is not None:
                Weapon = NPCDeathEvent.Weapon.Name
            else:
                Weapon = "some weapon"
            vloc = Victim.Location
            aloc = Attacker.Location
            dist = round(Util.GetVectorsDistance(vloc, aloc), 2)
            ini = self.DeathMSGConfig()
            sysname = ini.GetSetting("Settings", "SysName")
            sysnamecolor = str(ini.GetSetting("Settings", "SysNameColor"))
            msgcolor = str(ini.GetSetting("Settings", "MessageColor"))
            dmgmsg = ini.GetSetting("Settings", "AnimalDeath")
            dmgmsg = dmgmsg.replace("killer", AttackerName)
            dmgmsg = dmgmsg.replace("animal", VictimName)
            dmgmsg = dmgmsg.replace("dist", str(dist))
            dmgmsg = dmgmsg.replace("weapon", Weapon)
            self.SendTheMessage(sysname, dmgmsg, sysnamecolor, msgcolor)