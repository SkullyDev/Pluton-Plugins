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

class AdminList:
    def AdminListIniSettings(self):
        if not Plugin.IniExists("AdminListSettings"):
            ini = Plugin.CreateIni("AdminListSettings")
            ini.AddSetting("Settings", "Enabled", "1")
            ini.AddSetting("Settings", "AddAdminNameToMessage", "1")
            ini.AddSetting("Settings", "BroadcastMsgName", "AdminList")
            ini.Save()
        return Plugin.GetIni("AdminListSettings")

    def On_Command(self, cmd):
        if cmd.cmd == "admins":
            ini = self.AdminListIniSettings()
            if ini.GetSetting("Settings", "Enabled") == "1":
                sysname = ini.GetSetting("Settings", "BroadcastMsgName")
                if ini.GetSetting("Settings", "AddAdminNameToMessage") == "1":
                    i = 0
                    message = ""
                    for people in Server.ActivePlayers:
                        if people.Admin:
                            message = message + " " + people.Name
                            i = i + 1
                    cmd.User.MessageFrom(sysname, "ADMINS NOW ONLINE [" + str(i) + "]:" + str(message))
                else:
                    i = 0
                    for people in Server.ActivePlayers:
                        if people.Admin:
                            i = i + 1
                    cmd.User.MessageFrom(sysname, "ADMINS NOW ONLINE: " + str(i))