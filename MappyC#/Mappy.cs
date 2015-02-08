﻿using System;
using System.Timers;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using Pluton;
using Pluton.Events;
using UnityEngine;

namespace Mappy
{
    public class Mappy : CSharpPlugin
    {
        public void On_PluginInit()
        {
            DataStore.Flush("Mappy");
            IniParser ini = ConfigurationFile();
            if (ini.GetSetting("Settings", "enabled") == "1")
            {
                ServerConsoleCommands.Register("mappy").setCallback(GetCommand);
                string link = ini.GetSetting("Settings", "url");
                if (ini.GetSetting("Settings", "SendChat") == "1")
                {
                    DataStore.Add("Mappy", "SendChat", 1);
                    DataStore.Add("Mappy", "LinkChat", link + "chat.php");
                }
                DataStore.Add("Mappy", "Link", link + "server.php");
                DataStore.Add("Mappy", "LinkSize", link + "size.php");
                string mseconds = ini.GetSetting("Settings", "Timer");
                Plugin.CreateTimer("SendSizeOnce", 15000).Start();
                Plugin.CreateTimer("Send", mseconds.ToInt()).Start();
            }
        }

        public void GetCommand(string[] args)
        {
            if (args[0] != "")
            {
                if (args[0] == "airdrop")
                {
                    string x = args[1];
                    string z = args[2];
                    World.AirDropAt(float.Parse(x), 0, float.Parse(z));
                }
                
                else if (args[0] == "kick")
                {
                    string steamid = args[1];
                    Pluton.Player player = Pluton.Player.Find(steamid);
                    if (player != null)
                    {
                    player.Kick("Mappy control panel kick");
                    }
                }
                
                else if (args[0] == "message")
                {
                    string steamid = args[1];
                    Pluton.Player player = Pluton.Player.Find(steamid);
                    string message = string.Join(" ", args);
                    message = message.Replace(args[0] + " " + args[1] + " ", "");
                    player.Message(message);
                }
                
                else if (args[0] == "give")
                {
                    string steamid = args[1];
                    Pluton.Player player = Pluton.Player.Find(steamid);
                    int count = args[2].ToInt();
                    int item = Pluton.InvItem.GetItemID(args[3]);
                    player.Inventory.Add(item, count);
                }
                
                else if (args[0] == "teleport")
                {
                    string x = args[1];
                    string z = args[2];
                    string steamid = args[3];
                    Pluton.Player player = Pluton.Player.Find(steamid);
                    player.Teleport(float.Parse(x), World.GetGround(float.Parse(x), float.Parse(z)), float.Parse(z));
                }
                
                else if (args[0] == "animal")
                {
                    string x = args[1];
                    string z = args[2];
                    string animalname = args[3];
                    World.SpawnAnimal(animalname, float.Parse(x), float.Parse(z));
                }
                
                else if (args[0] == "broadcast")
                {
                    string message = string.Join(" ", args);
                    message = message.Replace(args[0] + " ", "");
                    Server.Broadcast(message);
                }
            }
            else
            {
                Logger.Log("MAPPY PLUGIN MADE BY SKULLY (REALLY HARD WORK)");
            }
        }

        private IniParser ConfigurationFile()
        {
            if (!Plugin.IniExists("ConfigurationFile"))
            {
                IniParser ini = Plugin.CreateIni("ConfigurationFile");
                ini.AddSetting("Settings", "enabled", "1");
                ini.AddSetting("Settings", "SendChat", "1");
                ini.AddSetting("Settings", "Timer", "60000");
                ini.AddSetting("Settings", "url", "http://www.example.com/mappy/");
                ini.Save();
            }
            return Plugin.GetIni("ConfigurationFile");
        }

        public void SendSizeOnceCallback(TimedEvent timer)
        {
            timer.Kill();
            DataStore.Add("Mappy", "SizeSent", 1);
            string link = (string)DataStore.Get("Mappy", "LinkSize");
            string WorldSize = "&worldsize=" + global::World.Size.ToString();
            Plugin.POST(link, WorldSize);
        }

        public void SendCallback(TimedEvent timer)
        {
            string ServersTime = World.Time.ToString();
            string plcount = Server.SleepingPlayers.Count.ToString();
            string post = "&time=" + ServersTime + "&sleepers=" + plcount;
            if ((int)DataStore.Get("Mappy", "SendChat") == 1)
            {
                post = post + "&showchat=true";
            }
            post = post + "&players=::";
            int i = 1;
            foreach (Pluton.Player player in Server.ActivePlayers)
            {
                string Name = player.Name;
                if (Name.Length < 2)
                {
                    string k = i.ToString();
                    Name = "Player - " + i.ToString();
                    i++;
                }
                else
                {
                    Name = Uri.EscapeDataString(Name);
                }
                string coords = player.Location.ToString();
                string stripit = coords.Replace(")", "");
                string stripit2 = coords.Replace("(", "");
                string stripit3 = coords.Replace(",", "");
                string[] splitted = stripit3.Split(' ');
                string coordx = splitted[0];
                string coordz = splitted[2];
                string steamid = player.SteamID;
                post = post + ";" + Name + ":" + coordx + ":" + coordz + ":" + steamid;
            }
            string link = (string)DataStore.Get("Mappy", "Link");
            Plugin.POST(link, post);
        }

        public void On_Chat(ChatEvent Chat)
        {
            if ((int)DataStore.Get("Mappy", "SendChat") == 1)
            {
                Pluton.Player  player = Chat.User;
                string Message = Uri.EscapeDataString(Chat.OriginalText);
                string Sender = player.Name;
                if (Sender.Length < 2)
                {
                    Sender = "Player";
                }
                else
                {
                    Sender = Uri.EscapeDataString(Sender);
                }
                string link = (string)DataStore.Get("Mappy", "LinkChat");
                string post = "&chat=" + Sender + ": " + Message;
                Plugin.POST(link, post);
            }
        }
    }
}