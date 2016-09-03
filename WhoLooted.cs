using System;
using System.IO;
using System.Timers;
using System.Collections;
using System.Collections.Generic;
using System.Runtime.Serialization.Formatters.Binary;
using UnityEngine;
using Pluton.Core;
using Pluton.Rust;
using Pluton.Rust.Events;
using Pluton.Rust.Objects;
using Pluton.Core.Serialize;
using Pluton.Rust.PluginLoaders;

namespace WhoLooted
{
    public class WhoLooted : CSharpPlugin
    {
        bool enabled = true;
        bool showTime = true;
        bool adminOnly = false;
        List<LootedLoot> lootedLoots;
        List<string> allowedLoots = new List<string>
        {
            "furnace_deployed.prefab",
            "lantern_deployed.prefab",
            "campfire_deployed.prefab",
            "woodbox_deployed.prefab",
            "large_woodbox_deployed.prefab",
            "researchtable_deployed.prefab",
            "repairbench_deployed.prefab"
        };

        public IniParser SettingsIni()
        {
            if (!Plugin.IniExists("Settings"))
            {
                IniParser ini = Plugin.CreateIni("Settings");
                ini.AddSetting("MainSettings", "Enabled", "1");
                ini.AddSetting("MainSettings", "AdminOnly", "0");
                ini.AddSetting("MainSettings", "ShowTimeWhenLooted", "1");
                ini.Save();
            }
            return Plugin.GetIni("Settings");
        }

        public void On_ServerInit()
        {
            LoadLootedLoots();
        }

        public void On_PluginInit()
        {
            Author = "SkullyDev";
            Version = "1.0";
            About = "";

            DataStore.Flush("WhoLooted");
            IniParser ini = SettingsIni();
            enabled = ini.GetSetting("MainSettings", "Enabled") == "1" ? true : false;
            adminOnly = ini.GetSetting("MainSettings", "AdminOnly") == "1" ? true : false;
            showTime = ini.GetSetting("MainSettings", "ShowTimeWhenLooted") == "1" ? true : false;
            if (!enabled) return;
            Commands.Register("wholooted").setCallback(WhoLootedCMD);
            if (Server.Instance.Loaded) LoadLootedLoots();
        }

        public void On_PluginDeinit()
        {
            SaveLootedLoots();
        }

        public void On_ServerShutdown()
        {
            SaveLootedLoots();
        }

        public void On_ServerSaved()
        {
            SaveLootedLoots();
        }

        public void On_LootingEntity(EntityLootEvent le)
        {
            if (!enabled) return;
            if (allowedLoots.Contains(le.Target.baseEntity.ShortPrefabName))
            {
                LootedLoot lootedLoot = new LootedLoot(le.Target.baseEntity, le.Looter.GameID);
                lootedLoots.Add(lootedLoot);
            }
        }

        public void On_BeingHammered(HammerEvent he)
        {
            if (!enabled || (adminOnly && !he.Player.Admin)) return;
            if (allowedLoots.Contains(he.Victim.baseEntity.ShortPrefabName) && DataStore.ContainsKey("WhoLooted", he.Player.GameID))
            {
                LootedLoot loot = TryToGetLoot(he.Victim.baseEntity);
                if (loot != null)
                {
                    if (loot.lastLooter == he.Player.GameID)
                    {
                        he.Player.Message("You were the last looter");
                    }
                    else
                    {
                        Player player = Server.Instance.Players[loot.lastLooter];
                        if (player == null)
                        {
                            he.Player.Message("We have some data but we don't remember his name! Sorry!");
                            return;
                        }
                        he.Player.Message("Last looter was " + player.Name);
                        if (showTime)
                        {
                            he.Player.Message("That happened in a " + loot.timeWhen.ToShortDateString() + " at " + loot.timeWhen.ToShortTimeString());
                        }
                        
                    }
                }
                else
                {
                    he.Player.Message("We have no data about this loot's history");
                }
            }
        }

        public void WhoLootedCMD(string[] args, Player player)
        {
            if (DataStore.ContainsKey("WhoLooted", player.GameID))
            {
                DataStore.Remove("WhoLooted", player.GameID);
                player.Message("WhoLooted was turned OFF");
            }
            else
            {
                DataStore.Add("WhoLooted", player.GameID, true);
                player.Message("WhoLooted was turned ON");
                player.Message("Using hammer hit loot box what you want to check");
            }
        }

        private LootedLoot TryToGetLoot(BaseEntity be)
        {
            foreach (LootedLoot lootedLoot in lootedLoots)
            {
                if (lootedLoot.AreEqual(be))
                {
                    return lootedLoot;
                }
            }
            return null;
        }

        private void LoadLootedLoots()
        {

            string path = Path.Combine(Util.GetPluginsFolder(), "WhoLooted\\LootedLoots.bin");
            lootedLoots = new List<LootedLoot>();
            if (!File.Exists(path)) return;
            try
            {
                FileInfo file = new FileInfo(path);
                using (FileStream stream = new FileStream(file.FullName, FileMode.Open))
                {
                    BinaryFormatter formatter = new BinaryFormatter();
                    lootedLoots = (List<LootedLoot>)formatter.Deserialize(stream);
                }
            }
            catch
            {
                Debug.LogError("[WhoLooted] Saved data can't be loaded because it's outdated!");
                Debug.LogError("[WhoLooted] All history about loots is now clear and unrecoverable!");
            }
        }

        private void SaveLootedLoots()
        {
            string path = Path.Combine(Util.GetPluginsFolder(), "WhoLooted\\LootedLoots.bin");
            using (FileStream stream = new FileStream(path, FileMode.Create))
            {
                BinaryFormatter formatter = new BinaryFormatter();
                formatter.Serialize(stream, lootedLoots);
            }
        }
    }

    [Serializable]
    internal class LootedLoot
    {
        public ulong lastLooter;
        public string prefabName;
        public DateTime timeWhen;
        public SerializedVector3 pos;
        public SerializedQuaternion rot;

        public LootedLoot(BaseEntity be, ulong steamID)
        {
            lastLooter = steamID;
            timeWhen = DateTime.Now;
            prefabName = be.ShortPrefabName;
            pos = new SerializedVector3(be.transform.position);
            rot = new SerializedQuaternion(be.transform.rotation);
        }

        public bool AreEqual(BaseEntity be)
        {
            if (this.prefabName == be.ShortPrefabName)
            {
                if (this.pos.ToVector3() == be.transform.position)
                {
                    if (this.rot.ToQuaternion() == be.transform.rotation)
                    {
                        return true;
                    }
                }
            }
            return false;
        }
    }
}