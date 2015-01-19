__author__ = 'DreTaX'
__version__ = '1.9.2'

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

"""
    Class
"""


class DeathMSG:
    """
        Brought to you by XCorrosionX and DreTaX
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

    def DeathMSGConfig(self):
        if not Plugin.IniExists("DeathMSGConfig"):
            loc = Plugin.CreateIni("DeathMSGConfig")
            loc.AddSetting("Settings", "SysName", "DeathMSG")
            loc.AddSetting("Settings", "NaturalDies", "1")
            loc.AddSetting("Settings", "KillLog", "1")
            loc.AddSetting("Settings", "AnimalKills", "1")
            loc.AddSetting("Settings", "Animal", "victim was killed by a killer")
            loc.AddSetting("Settings", "Suicide", "victim committed suicide...")
            loc.AddSetting("Settings", "Bite", "victim was bitten to death")
            loc.AddSetting("Settings", "BluntTrauma", "victim died from a blunt trauma")
            loc.AddSetting("Settings", "Heat", "victim burned to death")
            loc.AddSetting("Settings", "Hunger", "victim starved to death")
            loc.AddSetting("Settings", "Radiation", "victim died from radiation")
            loc.AddSetting("Settings", "Thirst", "victim died from thirst")
            loc.AddSetting("Settings", "Fall", "victim fell from a high place and died")
            loc.AddSetting("Settings", "Bleeding", "victim bled out")
            loc.AddSetting("Settings", "Beartrap", "victim ran into bear trap")
            loc.AddSetting("Settings", "Drowned", "victim drowned")
            loc.AddSetting("Settings", "Cold", "victim caught cold and died")
            loc.AddSetting("Settings", "Generic", "victim committed suicide...")
            loc.AddSetting("Settings", "Bullet", "killer shot victim in bodypart, from distm using weapon")
            loc.AddSetting("Settings", "Slash", "killer slashed victim in bodypart, from distm using weapon")
            loc.Save()
        return Plugin.GetIni("DeathMSGConfig")

    def On_PluginInit(self):
        self.DeathMSGConfig()

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
        if PlayerDeathEvent.Attacker.ToPlayer() is None:
            attacker = PlayerDeathEvent.Attacker
            animallongname = attacker.Name
            if animallongname == "Bleeding":
                ini = self.DeathMSGConfig()
                sysname = ini.GetSetting("Settings", "SysName")
                msg = ini.GetSetting("Settings", "Bleeding")
                msg = msg.replace("victim", PlayerDeathEvent.Victim.Name)
                Server.BroadcastFrom(sysname, msg)
                return
            animalname = self.IsEntity(animallongname)
            if animalname == "":
                return
            victim = PlayerDeathEvent.Victim
            victimname = victim.Name
            ini = self.DeathMSGConfig()
            if animalname == "fire":
                sysname = ini.GetSetting("Settings", "SysName")
                msg = ini.GetSetting("Settings", "Heat")
                msg = msg.replace("victim", victimname)
                Server.BroadcastFrom(sysname, msg)
                return
            if animalname == "beartrap":
                sysname = ini.GetSetting("Settings", "SysName")
                msg = ini.GetSetting("Settings", "Beartrap")
                msg = msg.replace("victim", victimname)
                Server.BroadcastFrom(sysname, msg)
                return
            Animal = ini.GetSetting("Settings", "AnimalKills")
            if Animal == "1":
                sysname = ini.GetSetting("Settings", "SysName")
                msg = ini.GetSetting("Settings", "Animal")
                msg = msg.replace("killer", animalname)
                msg = msg.replace("victim", victimname)
                Server.BroadcastFrom(sysname, msg)
        else:
            type = str(PlayerDeathEvent.DamageType)
            if type == "Bullet" or type == "Slash":
                attacker = PlayerDeathEvent.Attacker
                victim = PlayerDeathEvent.Victim
                attackername = attacker.Name
                victimname = victim.Name
                ini = self.DeathMSGConfig()
                sysname = ini.GetSetting("Settings", "SysName")
                weapon = PlayerDeathEvent.Weapon.Name
                dmgmsg = ini.GetSetting("Settings", type)
                bodypart = str(PlayerDeathEvent.HitBone)
                bpart = self.BodyParts.get(bodypart, bodypart)
                vloc = victim.Location
                aloc = attacker.Location
                dist = round(Util.GetVectorsDistance(vloc, aloc), 2)
                dmgmsg = dmgmsg.replace("killer", attackername)
                dmgmsg = dmgmsg.replace("victim", victimname)
                dmgmsg = dmgmsg.replace("dist", str(dist))
                dmgmsg = dmgmsg.replace("weapon", weapon)
                dmgmsg = dmgmsg.replace("bodypart", bpart)
                KillLog = int(ini.GetSetting("Settings", "KillLog"))
                Server.BroadcastFrom(sysname, dmgmsg)
                if KillLog == 1:
                    Plugin.Log("KillLog", str(System.DateTime.Now) + " " + dmgmsg)
            else:
                ini = self.DeathMSGConfig()
                NaturalDies = int(ini.GetSetting("Settings", "NaturalDies"))
                if NaturalDies == 1:
                    victim = PlayerDeathEvent.Victim
                    victimname = str(victim.Name)
                    if victimname == None or victimname == "":
                        return
                    sysname = ini.GetSetting("Settings", "SysName")
                    msg = ini.GetSetting("Settings", type)
                    msg = msg.replace("victim", victimname)
                    Server.BroadcastFrom(sysname, msg)