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
        'items/campfire_deployed': 'fire',
        'items/grenade.f1.deployed': 'F1 grenade',
        'items/items/grenade.beancan.deployed': 'beancan grenade',
        'items/timed.explosive.deployed': 'timed explosive',
        'items/rocket_basic': 'rocket',
        'items/rocket_hv': 'rocket',
        'items/floor_spikes': 'floor spikes',
        'items/barricades/barricade.wood': 'wooden barricade',
        'items/barricades/barricade.woodwire': 'wired wooden barricade',
        'items/barricades/barricade.metal': 'metal barricade',
        'autospawn/animals/bear': 'bear',
        'autospawn/animals/wolf': 'wolf',
        'autospawn/animals/stag': 'stag',
        'autospawn/animals/boar': 'boar',
        'autospawn/animals/horse': 'horse',
        'autospawn/animals/chicken': 'chicken'
    }
    
    Types = {
        'Suicide': 'victim was punished by gods...',
        'Heat': 'victim burned to death',
        'Poison': 'victim poisoned him self to death',
        'Hunger': 'victim starved to death',
        'Radiation': 'victim died from radiation',
        'RadiationExposure': 'victim died from radiation exposure',
        'Thirst': 'victim died from thirst',
        'Fall': 'victim fell from a high place and died',
        'Bleeding': 'victim bled out',
        'Drowned': 'victim drowned',
        'Cold': 'victim froze to death',
        'ColdExposure': 'victim died from cold exposure'
    }
    
    KillLog = 1
    NaturalDies = 1
    AnimalKills = 1
    AnimalDeaths = 1
    SleepingKills = 1
    MessageColor = "red"

    def SendTheMessage(self, msg):
        Server.BroadcastFrom(0, "<color=#FFAA55>DEATH & KILL</color>: <color=" + self.MessageColor + ">" + msg + "</color>")

    def On_PlayerDied(self, PlayerDeathEvent):
        #print(str(PlayerDeathEvent.DamageType))
        #print(PlayerDeathEvent.Victim.Name)
        type = str(PlayerDeathEvent.DamageType)
        Victim = PlayerDeathEvent.Victim
        VictimName = Victim.Name
        Sleeping = Victim.basePlayer.IsSleeping()
        msgcolor = self.MessageColor
        if PlayerDeathEvent.Attacker is None:
            if type == "Bite":
                msg = "victim ran in to the bear trap"
                msg = msg.replace("victim", "</color>" + VictimName + "<color=" + msgcolor + ">")
                self.SendTheMessage(msg)
                if self.KillLog == 1:
                    Plugin.Log("KillLog", str(System.DateTime.Now) + " " + msg)
            elif type == "Bleeding":
                if Sleeping:
                    msg = "victim bled out while he was sleeping"
                else:
                    msg = "victim bled out"
                msg = msg.replace("victim", "</color>" + VictimName + "<color=" + msgcolor + ">")
                self.SendTheMessage(msg)
                if self.KillLog == 1:
                    Plugin.Log("KillLog", str(System.DateTime.Now) + " " + msg)
            else:
                if self.NaturalDies == 1:
                    msg = self.Types.get(type, type)
                    msg = msg.replace("victim", "</color>" + VictimName + "<color=" + msgcolor + ">")
                    self.SendTheMessage(msg)
                    if self.KillLog == 1:
                        Plugin.Log("KillLog", str(System.DateTime.Now) + " " + msg)
        else:
            #print(PlayerDeathEvent.Attacker.Name)
            #if PlayerDeathEvent.Weapon is not None:
            #    print(PlayerDeathEvent.Weapon.Name)
            Attacker = PlayerDeathEvent.Attacker
            AttackerName = Attacker.Name
            if Attacker.ToPlayer() is None:
                AttackerName = self.Objects.get(AttackerName, AttackerName)
                if AttackerName == Attacker.Name:
                    AttackerName = "something"
                elif type == "Explosion":
                    if Sleeping:
                        msg = "victim was blown up by killer while he was sleeping"
                    else:
                        msg = "victim was blown up by killer"
                    msg = msg.replace("victim", "</color>" + VictimName + "<color=" + msgcolor + ">")
                    msg = msg.replace("killer", AttackerName)
                    self.SendTheMessage(msg)
                    if self.KillLog == 1:
                        Plugin.Log("KillLog", str(System.DateTime.Now) + " " + msg)
                elif type == "Slash":
                    msg = "victim ran in to killer and bled out"
                    msg = msg.replace("victim", "</color>" + VictimName + "<color=" + msgcolor + ">")
                    msg = msg.replace("killer", AttackerName)
                    self.SendTheMessage(msg)
                    if self.KillLog == 1:
                        Plugin.Log("KillLog", str(System.DateTime.Now) + " " + msg)
                elif type == "Stab":
                    msg = "victim ran in to killer and bled out"
                    msg = msg.replace("victim", "</color>" + VictimName + "<color=" + msgcolor + ">")
                    msg = msg.replace("killer", AttackerName)
                    self.SendTheMessage(msg)
                    if self.KillLog == 1:
                        Plugin.Log("KillLog", str(System.DateTime.Now) + " " + msg)
                elif type == "Bite":
                    if self.AnimalKills == 1:
                        if Sleeping:
                            msg = "victim was bitten to death while he was sleeping by killer"
                        else:
                            msg = "victim was bitten to death by killer"
                        msg = msg.replace("killer", AttackerName)
                        msg = msg.replace("victim", "</color>" + VictimName + "<color=" + msgcolor + ">")
                        self.SendTheMessage(msg)
                        if self.KillLog == 1:
                            Plugin.Log("KillLog", str(System.DateTime.Now) + " " + msg)
            else:
                if Victim.IsWounded:
                    if type == "Bullet":
                        if PlayerDeathEvent.Weapon is not None:
                            Weapon = PlayerDeathEvent.Weapon.Name
                        else:
                            Weapon = "some weapon"
                        if Sleeping:
                            dmgmsg = "killer shot victim while he was sleeping in bodypart, from distm using weapon"
                        else:
                            dmgmsg = "killer shot victim in bodypart, from distm using weapon"
                        bodypart = str(PlayerDeathEvent.HitBone)
                        bpart = self.BodyParts.get(bodypart, bodypart)
                        if bodypart == bpart and not bodypart == "head" and not bodypart == "neck":
                            bpart = "body"
                        vloc = Victim.Location
                        aloc = Attacker.Location
                        dist = round(Util.GetVectorsDistance(vloc, aloc), 2)
                        dmgmsg = dmgmsg.replace("killer", "</color>" + AttackerName + "<color=" + msgcolor + ">")
                        dmgmsg = dmgmsg.replace("victim", "</color>" + VictimName + "<color=" + msgcolor + ">")
                        dmgmsg = dmgmsg.replace("dist", str(dist))
                        if PlayerDeathEvent.Weapon is not None:
                            Weapon = PlayerDeathEvent.Weapon.Name
                        else:
                            Weapon = "some weapon"
                        dmgmsg = dmgmsg.replace("weapon", Weapon)
                        dmgmsg = dmgmsg.replace("bodypart", bpart)
                        self.SendTheMessage(dmgmsg)
                        if self.KillLog == 1:
                            Plugin.Log("KillLog", str(System.DateTime.Now) + " " + dmgmsg)
                    elif type == "Blunt":
                        if PlayerDeathEvent.Weapon is not None:
                            Weapon = PlayerDeathEvent.Weapon.Name
                        else:
                            Weapon = "some weapon"
                        if Sleeping:
                            dmgmsg = "killer hit victim while he was sleeping in bodypart using weapon"
                        else:
                            dmgmsg = "killer hit victim in bodypart using weapon"
                        bodypart = str(PlayerDeathEvent.HitBone)
                        bpart = self.BodyParts.get(bodypart, bodypart)
                        if bodypart == bpart and not bodypart == "head" and not bodypart == "neck":
                            bpart = "body"
                        vloc = Victim.Location
                        aloc = Attacker.Location
                        dist = round(Util.GetVectorsDistance(vloc, aloc), 2)
                        dmgmsg = dmgmsg.replace("killer", "</color>" + AttackerName + "<color=" + msgcolor + ">")
                        dmgmsg = dmgmsg.replace("victim", "</color>" + VictimName + "<color=" + msgcolor + ">")
                        dmgmsg = dmgmsg.replace("weapon", Weapon)
                        dmgmsg = dmgmsg.replace("bodypart", bpart)
                        self.SendTheMessage(dmgmsg)
                        if self.KillLog == 1:
                            Plugin.Log("KillLog", str(System.DateTime.Now) + " " + dmgmsg)
                    elif type == "Stab":
                        if PlayerDeathEvent.Weapon is not None:
                            Weapon = PlayerDeathEvent.Weapon.Name
                        else:
                            Weapon = "some weapon"
                        if Weapon == "Hunting Bow":
                            if Sleeping:
                                dmgmsg = "killer shot victim while he was sleeping in bodypart, from distm using weapon"
                            else:
                                dmgmsg = "killer shot victim in bodypart, from distm using weapon"
                        else:
                            if Sleeping:
                                dmgmsg = "killer hit victim while he was sleeping in bodypart using weapon"
                            else:
                                dmgmsg = "killer hit victim in bodypart using weapon"
                        bodypart = str(PlayerDeathEvent.HitBone)
                        bpart = self.BodyParts.get(bodypart, bodypart)
                        if bodypart == bpart and not bodypart == "head" and not bodypart == "neck":
                            bpart = "body"
                        vloc = Victim.Location
                        aloc = Attacker.Location
                        dist = round(Util.GetVectorsDistance(vloc, aloc), 2)
                        dmgmsg = dmgmsg.replace("killer", "</color>" + AttackerName + "<color=" + msgcolor + ">")
                        dmgmsg = dmgmsg.replace("victim", "</color>" + VictimName + "<color=" + msgcolor + ">")
                        dmgmsg = dmgmsg.replace("dist", str(dist))
                        dmgmsg = dmgmsg.replace("weapon", Weapon)
                        dmgmsg = dmgmsg.replace("bodypart", bpart)
                        self.SendTheMessage(dmgmsg)
                        if self.KillLog == 1:
                            Plugin.Log("KillLog", str(System.DateTime.Now) + " " + dmgmsg)
                    elif type == "Slash":
                        if PlayerDeathEvent.Weapon is not None:
                            Weapon = PlayerDeathEvent.Weapon.Name
                        else:
                            Weapon = "some weapon"
                        if Sleeping:
                            dmgmsg = "killer slashed victim while he was sleeping in bodypart, from distm using weapon"
                        else:
                            dmgmsg = "killer slashed victim in bodypart, from distm using weapon"
                        bodypart = str(PlayerDeathEvent.HitBone)
                        bpart = self.BodyParts.get(bodypart, bodypart)
                        if bodypart == bpart and not bodypart == "head" and not bodypart == "neck":
                            bpart = "body"
                        vloc = Victim.Location
                        aloc = Attacker.Location
                        dist = round(Util.GetVectorsDistance(vloc, aloc), 2)
                        dmgmsg = dmgmsg.replace("killer", "</color>" + AttackerName + "<color=" + msgcolor + ">")
                        dmgmsg = dmgmsg.replace("victim", "</color>" + VictimName + "<color=" + msgcolor + ">")
                        dmgmsg = dmgmsg.replace("dist", str(dist))
                        dmgmsg = dmgmsg.replace("weapon", Weapon)
                        dmgmsg = dmgmsg.replace("bodypart", bpart)
                        self.SendTheMessage(dmgmsg)
                        if self.KillLog == 1:
                            Plugin.Log("KillLog", str(System.DateTime.Now) + " " + dmgmsg)

    def On_NPCKilled(self, NPCDeathEvent):
        if NPCDeathEvent.Attacker is None:
            return
        if NPCDeathEvent.Attacker.ToPlayer() is None:
            return
        #print(str(NPCDeathEvent.DamageType))
        #print(NPCDeathEvent.Victim.Name)
        #print(NPCDeathEvent.Attacker.ToPlayer().Name)
        if self.AnimalKills == 1:
            Victim = NPCDeathEvent.Victim
            Attacker = NPCDeathEvent.Attacker.ToPlayer()
            VictimName = "poor " + self.Objects.get(Victim.Name, Victim.Name)
            AttackerName = Attacker.Name
            if NPCDeathEvent.Weapon is not None:
                #print(NPCDeathEvent.Weapon.Name)
                Weapon = NPCDeathEvent.Weapon.Name
            else:
                Weapon = "some weapon"
            dmgmsg = "killer killed animal using weapon"
            dmgmsg = dmgmsg.replace("killer", "</color>" + AttackerName + "<color=" + self.MessageColor + ">")
            dmgmsg = dmgmsg.replace("animal", VictimName)
            dmgmsg = dmgmsg.replace("weapon", Weapon)
            self.SendTheMessage(dmgmsg)