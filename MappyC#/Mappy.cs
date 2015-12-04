using System;
using Pluton;
using UnityEngine;

namespace Mappy
{
    public class Mappy : CSharpPlugin
    {
        public void On_PluginInit()
        {
            if (!Server.Loaded) return;
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
                else
                {
                    DataStore.Add("Mappy", "SendChat", 0);
                }
                DataStore.Add("Mappy", "Link", link + "server.php");
                DataStore.Add("Mappy", "LinkSize", link + "size.php");
                int mseconds = ToInt(ini.GetSetting("Settings", "Timer"));
                StartPlugin(mseconds);
            }
        }

        public void On_ServerInit()
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
                else
                {
                    DataStore.Add("Mappy", "SendChat", 0);
                }
                DataStore.Add("Mappy", "Link", link + "server.php");
                DataStore.Add("Mappy", "LinkSize", link + "size.php");
                int mseconds = ToInt(ini.GetSetting("Settings", "Timer"));
                StartPlugin(mseconds);
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
                        ulong sid = UInt64.Parse(args[1]);
                        if (Server.Players.ContainsKey(sid))
                        {
                            Pluton.Player player = Server.Players[sid];
                            string message = String.Join(" ", args);
                            message = String.Format("{0}", message.Replace(args[0] + " " + args[1] + " ", ""));
                            player.Kick(message);
                        }
                    }
                }

                else if (args[0] == "ban")
                {
                    if (args.Length >= 2)
                    {
                        ulong sid = UInt64.Parse(args[1]);
                        if (Server.Players.ContainsKey(sid))
                        {
                            Pluton.Player player = Server.Players[sid];
                            string message = String.Join(" ", args);
                            message = String.Format("{0}", message.Replace(args[0] + " " + args[1] + " ", ""));
                            player.Ban(message);
                        }
                    }
                }

                else if (args[0] == "message")
                {
                    if (args.Length >= 3)
                    {
                        ulong sid = UInt64.Parse(args[1]);
                        if (Server.Players.ContainsKey(sid))
                        {
                            Pluton.Player player = Server.Players[sid];
                            string message = String.Join(" ", args);
                            message = String.Format("{0}", message.Replace(args[0] + " " + args[1] + " ", ""));
                            player.Message(message);
                        }
                    }
                }

                else if (args[0] == "give")
                {
                    if (args.Length >= 4)
                    {
                        ulong sid = UInt64.Parse(args[1]);
                        if (Server.Players.ContainsKey(sid))
                        {
                            Pluton.Player player = Server.Players[sid];
                            int count = ToInt(args[2]);
                            int item = 0;
                            item = Pluton.InvItem.GetItemID(args[3]);
                            if (item == 0)
                                return;
                            player.Inventory.Add(item, count);
                        }
                    }
                }

                else if (args[0] == "teleport")
                {
                    if (args.Length >= 4)
                    {
                        ulong sid = UInt64.Parse(args[1]);
                        if (Server.Players.ContainsKey(sid))
                        {
                            Pluton.Player player = Server.Players[sid];
                            String x = args[2];
                            String z = args[3];
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
                        GameManager.server.CreateEntity("autospawn/animals/" + animalname, new UnityEngine.Vector3(x, World.GetGround(x, z), z)).Spawn(true);
                    }
                }

                else if (args[0] == "broadcast")
                {
                    if (args.Length >= 2)
                    {
                        string message = String.Join(" ", args);
                        message = String.Format("{0}", message.Replace(args[0] + " ", ""));
                        Server.Broadcast(message);
                    }
                }
            }
            else
            {
                Logger.Log("MAPPY PLUGIN & MAP CODE MADE BY Skully (SkullyDev)");
                Logger.Log("Proud member of Pluton-Team.ORG");
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

        private void StartPlugin(int ms)
        {
            Plugin.CreateTimer("Send", ms).Start();
            string link = (string)DataStore.Get("Mappy", "LinkSize");
            string WorldSize = String.Format("&worldsize={0}", global::World.Size.ToString());
            Plugin.POST(link, WorldSize);
        }

        public void SendCallback(TimedEvent timer)
        {
            string post = String.Format("&time={0}&sleepers={1}", World.Time.ToString(), Server.SleepingPlayers.Count.ToString());
            if ((int)DataStore.Get("Mappy", "SendChat") == 1)
            {
                post = String.Format("{0}&showchat=true", post);
            }
            post = String.Format("{0}&players=::", post);
            foreach (Pluton.Player player in Server.ActivePlayers)
            {
                post = String.Format("{0};{1}:{2}:{3}:{4}", post, Uri.EscapeDataString(player.Name), player.X, player.Z, player.SteamID);
            }
            string link = (string)DataStore.Get("Mappy", "Link");
            try { Plugin.POST(link, post); } catch { }
        }

        public void On_Chat(Pluton.Events.ChatEvent Chat)
        {
            if ((int)DataStore.Get("Mappy", "SendChat") == 1)
            {
                Pluton.Player player = Chat.User;
                string post = String.Format("&chat={0}: {1}", Uri.EscapeDataString(player.Name), Uri.EscapeDataString(Chat.OriginalText));
                string link = (string)DataStore.Get("Mappy", "LinkChat");
                try { Plugin.POST(link, post); } catch { }
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