using System;
using UnityEngine;
using Pluton.Core;
using Pluton.Rust;
using Pluton.Rust.Events;
using Pluton.Rust.Objects;
using Pluton.Rust.PluginLoaders;

namespace Mappy
{
    public class Mappy : CSharpPlugin
    {
        bool chatEnabled = false;
        string Link = string.Empty;
        string LinkSize = string.Empty;
        string LinkChat = string.Empty;

        public void On_PluginInit()
        {
            Author = "SkullyDev";
            Version = "1.0";
            About = "";

            if (!Server.Instance.Loaded) return;
            LoadPlugin();
        }

        public void On_ServerInit()
        {
            LoadPlugin();
        }

        private void LoadPlugin()
        {
            IniParser ini = ConfigurationFile();
            if (ini.GetSetting("Settings", "enabled") == "1")
            {
                string link = ini.GetSetting("Settings", "url");
                ServerConsoleCommands.Register("mappy").setCallback(GetCommand);
                if (ini.GetSetting("Settings", "SendChat") == "1")
                {
                    chatEnabled = true;
                    LinkChat = link + "chat.php";
                }
                Link = link + "server.php";
                LinkSize = link + "size.php";
                int mseconds = ToInt(ini.GetSetting("Settings", "Timer"));
                Plugin.CreateTimer("MappySend", mseconds).Start();
                string WorldSize = string.Format("&worldsize={0}", global::World.Size.ToString());
                Plugin.POST(LinkSize, WorldSize);
            }
        }

        public void GetCommand(string[] args)
        {
            if (args[0] != "")
            {
                if (args[0] == "airdrop")
                {
                    if (args.Length >= 3)
                    {
                        string x = args[1];
                        string z = args[2];
                        World.AirDropAt(float.Parse(x), 0, float.Parse(z));
                    }
                }

                else if (args[0] == "kick")
                {
                    if (args.Length >= 2)
                    {
                        ulong sid = ulong.Parse(args[1]);
                        if (Server.Instance.Players.ContainsKey(sid))
                        {
                            Player player = Server.Instance.Players[sid];
                            string message = string.Join(" ", args);
                            message = string.Format("{0}", message.Replace(args[0] + " " + args[1] + " ", ""));
                            player.Kick(message);
                        }
                    }
                }

                else if (args[0] == "ban")
                {
                    if (args.Length >= 2)
                    {
                        ulong sid = ulong.Parse(args[1]);
                        if (Server.Instance.Players.ContainsKey(sid))
                        {
                            Player player = Server.Instance.Players[sid];
                            string message = string.Join(" ", args);
                            message = string.Format("{0}", message.Replace(args[0] + " " + args[1] + " ", ""));
                            player.Ban(message);
                        }
                    }
                }

                else if (args[0] == "message")
                {
                    if (args.Length >= 3)
                    {
                        ulong sid = ulong.Parse(args[1]);
                        if (Server.Instance.Players.ContainsKey(sid))
                        {
                            Player player = Server.Instance.Players[sid];
                            string message = string.Join(" ", args);
                            message = string.Format("{0}", message.Replace(args[0] + " " + args[1] + " ", ""));
                            player.Message(message);
                        }
                    }
                }

                else if (args[0] == "give")
                {
                    if (args.Length >= 4)
                    {
                        ulong sid = ulong.Parse(args[1]);
                        if (Server.Instance.Players.ContainsKey(sid))
                        {
                            Player player = Server.Instance.Players[sid];
                            int count = ToInt(args[2]);
                            int item = 0;
                            item = InvItem.GetItemID(args[3]);
                            if (item == 0) return;
                            player.Inventory.Add(item, count);
                        }
                    }
                }

                else if (args[0] == "teleport")
                {
                    if (args.Length >= 4)
                    {
                        ulong sid = ulong.Parse(args[1]);
                        if (Server.Instance.Players.ContainsKey(sid))
                        {
                            Player player = Server.Instance.Players[sid];
                            string x = args[2];
                            string z = args[3];
                            player.Teleport(float.Parse(x), World.GetGround(float.Parse(x), float.Parse(z)), float.Parse(z));
                        }
                    }
                }

                else if (args[0] == "animal")
                {
                    if (args.Length >= 4)
                    {
                        float x = float.Parse(args[1]);
                        float z = float.Parse(args[2]);
                        string animalname = args[3];
                        GameManager.server.CreateEntity("autospawn/animals/" + animalname, new Vector3(x, World.GetGround(x, z), z)).Spawn(true);
                    }
                }

                else if (args[0] == "broadcast")
                {
                    if (args.Length >= 2)
                    {
                        string message = string.Join(" ", args);
                        message = string.Format("{0}", message.Replace(args[0] + " ", ""));
                        Server.Instance.Broadcast(message);
                    }
                }
            }
            else
            {
                Pluton.Core.Logger.Log("MAPPY PLUGIN & MAP CODE MADE BY Skully (SkullyDev)");
                Pluton.Core.Logger.Log("Proud member of Pluton-Team.ORG");
            }
        }

        private IniParser ConfigurationFile()
        {
            if (!Plugin.IniExists("ConfigurationFile"))
            {
                IniParser ini = Plugin.CreateIni("ConfigurationFile");
                ini.AddSetting("Settings", "enabled", "1");
                ini.AddSetting("Settings", "SendChat", "1");
                ini.AddSetting("Settings", "Timer", "5000");
                ini.AddSetting("Settings", "url", "http://www.example.com/mappy/");
                ini.Save();
            }
            return Plugin.GetIni("ConfigurationFile");
        }

        public void MappySendCallback(TimedEvent timer)
        {
            string post = string.Format("&time={0}&sleepers={1}", TOD_Sky.Instance.Cycle.Hour.ToString(), Server.Instance.SleepingPlayers.Count.ToString());
            if (chatEnabled) post = string.Format("{0}&showchat=true", post);
            post = string.Format("{0}&players=::", post);
            foreach (Player player in Server.Instance.ActivePlayers) post = string.Format("{0};{1}:{2}:{3}:{4}", post, Uri.EscapeDataString(player.Name), player.X, player.Z, player.SteamID);
            try { Plugin.POST(Link, post); } catch { }
        }

        public void On_Chat(ChatEvent Chat)
        {
            if (chatEnabled)
            {
                Player player = Chat.User;
                string post = string.Format("&chat={0}: {1}", Uri.EscapeDataString(player.Name), Uri.EscapeDataString(Chat.OriginalText));
                try { Plugin.POST(LinkChat, post); } catch { }
            }
        }

        private int ToInt(string obj)
        {
            int i;
            int.TryParse(obj, out i);
            return i;
        }
    }
}