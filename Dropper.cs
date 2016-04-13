using System;
using System.Collections.Generic;
using UnityEngine;
using Pluton.Core;
using Pluton.Rust;
using Pluton.Rust.Events;
using Pluton.Rust.Objects;
using Pluton.Rust.PluginLoaders;

namespace Dropper
{
    public class Dropper : CSharpPlugin
    {
        private string sysName = "Dropper";
        private bool showDropPos = false;
        private string dropPosMsg = "SUPPLY DROP WAS DROPPED AT";
        private string prefab = "assets/prefabs/npc/cargo plane/cargo_plane.prefab";

        public class DropperPlane : MonoBehaviour
        {
            public int droppedCount = 0;
            public bool[] dropped;
            public string sysName;
            public int dropCountTotal;
            public Vector3 lookAt;
            public Vector3[] dropPoints;
            public BaseEntity plane;
            public string dropPosMsg;
            public bool showDropPos = false;
            public float wsize = global::World.Size;
			
			public void Kill() { SendMessage("KillMessage", 1); }

            void Update()
            {
                if (!dropped[droppedCount] && Vector3.Distance(transform.position, dropPoints[droppedCount]) <= 1f) {
                    BaseEntity baseEntity = GameManager.server.CreateEntity("assets/prefabs/misc/supply drop/supply_drop.prefab", transform.position);
                    baseEntity.globalBroadcast = true;
                    baseEntity.Spawn();
                    if (showDropPos) {
                        string posmsg = string.Format("X: {0} Z: {1}", ((int)(transform.position.x)).ToString(), ((int)(transform.position.z)).ToString());
                        ConsoleSystem.Broadcast("chat.add", 0, string.Format("{0}: {1} {2}", sysName.ColorText("fa5"), dropPosMsg, posmsg));
                    }
                    dropped[droppedCount] = true;
                    if (dropped[dropCountTotal]) {
                        lookAt = dropPoints[dropCountTotal + 1];
                    } else {
                        droppedCount++;
                        lookAt = dropPoints[droppedCount];
                    }

                }
                else if (!dropped[droppedCount] && Vector3.Distance(transform.position, dropPoints[droppedCount]) <= 100f) {
                    transform.LookAt(dropPoints[droppedCount], new Vector3(0, transform.position.y, 0));
                }
                Quaternion rotatePoint = Quaternion.LookRotation(lookAt - transform.position);
                transform.rotation = Quaternion.Slerp(transform.rotation, rotatePoint, 0.3f * Time.deltaTime);
                Vector3 forward = transform.position + transform.forward;
                forward.y = transform.position.y;
                transform.position = Vector3.MoveTowards(transform.position, forward, 50f * Time.deltaTime);
                plane.TransformChanged();
                if (dropped[dropCountTotal] && (transform.position.x >= wsize - 1 || transform.position.z >= wsize - 1 || transform.position.x <= -(wsize - 1) || transform.position.z <= -(wsize - 1))) {
                    SendMessage("KillMessage", 1);
                }
            }
        }

        private IniParser DropperIniSettings()
        {
            if (!Plugin.IniExists("DropperSettings")) {
                IniParser ini = Plugin.CreateIni("DropperSettings");
                ini.AddSetting("Settings", "Enabled", "1");
                ini.AddSetting("Settings", "EventEveryMins", "30");
                ini.AddSetting("Settings", "PlayersNeeded", "5");
                ini.AddSetting("Settings", "PlanesInSameTime", "1");
                ini.AddSetting("Settings", "DropsFromOnePlane", "1");
                ini.AddSetting("Settings", "DropPositionMessage", "1");
                ini.AddSetting("Settings", "BroadcastMsgName", "Dropper");
                ini.AddSetting("Settings", "DropPositionMessageText", "SUPPLY DROP WAS DROPPED AT");
                ini.AddSetting("Settings", "BroadcastMsgLowPlayers", "AIRDROP WAS CANCELLED, NEED MORE PLAYERS");
                ini.AddSetting("Settings", "BroadcastMsgAirdropIncoming", "AIRDROP CARGO PLANE INCOMING");
                ini.Save();
            }
            return Plugin.GetIni("DropperSettings");
        }

        public void On_EventTriggered(EventTriggeredEvent ete) { if (ete.Prefab == prefab) ete.Stop = true; }

        public void On_PluginInit()
        {
            Author = "SkullyDev";
            Version = "4.6.5";
            About = "Custom planes, multiple drop function, plane manipulation, timed events.";
            
            Commands.Register("airdrop").setCallback(SpawnPlaneChatCMD);
            ServerConsoleCommands.Register("airdrop").setCallback(SpawnPlaneConsoleCMD);
            IniParser ini = DropperIniSettings();
            if (ini.GetSetting("Settings", "Enabled") == "1") {
                if (ini.GetSetting("Settings", "DropPositionMessage") == "1") {
                    showDropPos = true;
                    dropPosMsg = ini.GetSetting("Settings", "DropPositionMessageText");
                }
                sysName = ini.GetSetting("Settings", "BroadcastMsgName");
                int mins = int.Parse(ini.GetSetting("Settings", "EventEveryMins"));
                Plugin.CreateTimer("Drop", mins * 60000).Start();
                Pluton.Core.Logger.Log("[DROPPER] PLUGIN WAS LOADED AND EVENT TIMER STARTED");
            }
        }

        public void DropCallback(TimedEvent timer)
        {
            IniParser ini = DropperIniSettings();
            int online = Server.Instance.Players.Count;
            int needed = int.Parse(ini.GetSetting("Settings", "PlayersNeeded"));
            if (online >= needed) {
                int drops = int.Parse(ini.GetSetting("Settings", "DropsFromOnePlane"));
                int planes = int.Parse(ini.GetSetting("Settings", "PlanesInSameTime"));
                for (int i = 1; i <= planes; i++) SpawnPlane(drops);
                string message = ini.GetSetting("Settings", "BroadcastMsgAirdropIncoming");
                Server.Instance.BroadcastFrom(sysName, message);
                Pluton.Core.Logger.Log("[EVENT] AIRDROP CARGO PLANE IN SERVER");
            } else { Server.Instance.BroadcastFrom(sysName, ini.GetSetting("Settings", "BroadcastMsgLowPlayers")); }
        }

        public void SpawnPlaneChatCMD(string[] args, Player player)
        {
            if (player.Admin) {
                SpawnPlane();
                player.Message("AIRDROP CARGO PLANE IN SERVER");
                Pluton.Core.Logger.Log("[EVENT] AIRDROP CARGO PLANE IN SERVER");
            } else { player.Message("You are not allowed to use this command"); }
        }

        public void SpawnPlaneConsoleCMD(string[] args)
        {
            SpawnPlane();
            Pluton.Core.Logger.Log("[EVENT] AIRDROP CARGO PLANE IN SERVER");
        }

        public void SpawnPlane(int drops = 1)
        {
            float worldsize = global::World.Size;
            float y = 1000f;
            Vector3 startingpos = default(Vector3);
            float pos = UnityEngine.Random.Range(-worldsize / 3, worldsize / 3);
            int rand = UnityEngine.Random.Range(1, 100);
            int rand2 = UnityEngine.Random.Range(1, 100);
            if (rand >= 50) {
                startingpos.x = pos;
                if (rand2 <= 50) startingpos.z = worldsize;
                else startingpos.z = -worldsize;
            } else {
                startingpos.z = pos;
                if (rand2 <= 50) startingpos.x = worldsize;
                else startingpos.x = -worldsize;
            }
            startingpos.y = y;
            Vector3[] droppingpoints = new Vector3[drops + 1];
            droppingpoints[drops] = startingpos;
            for (int i = 0; i < drops; i++) {
                bool regenerate = true;
                while (regenerate) {
                    RaycastHit hit;
                    float x = UnityEngine.Random.Range(-worldsize, worldsize);
                    float z = UnityEngine.Random.Range(-worldsize, worldsize);
                    var origin = new Vector3(x, 1000f, z);
                    if (Physics.Raycast(origin, Vector3.down, out hit, 1100f, 1 << 23)) {
                        if (hit.point.y > 0f) {
                            Vector3 newpoint = new Vector3(x, y, z);
                            foreach (Vector3 point in droppingpoints) {
                                if (point == null || point == default(Vector3) || Vector3.Distance(newpoint, point) >= 150f) {
                                    regenerate = false;
                                    droppingpoints[i].x = x;
                                    droppingpoints[i].y = y;
                                    droppingpoints[i].z = z;
                                }
                            }
                        }
                    }
                }
            }
            BaseEntity baseEntity = GameManager.server.CreateEntity(prefab, startingpos, Quaternion.LookRotation(droppingpoints[0]));
            baseEntity.Spawn();
            CargoPlane[] cp = baseEntity.GetComponents<CargoPlane>();
            foreach (CargoPlane each in cp) each.enabled = false;
            baseEntity.transform.position = startingpos;
            baseEntity.transform.LookAt(droppingpoints[0], new Vector3(0,y,0));
            baseEntity.TransformChanged();
            DropperPlane classy = baseEntity.gameObject.AddComponent<DropperPlane>();
            classy.dropPoints = new Vector3[drops + 1];
            classy.dropped = new bool[drops];
            classy.dropPoints = droppingpoints;
            classy.lookAt = droppingpoints[0];
            classy.dropCountTotal = drops - 1;
            classy.plane = baseEntity;
            if (showDropPos) {
                classy.dropPosMsg = dropPosMsg;
                classy.showDropPos = showDropPos;
                classy.sysName = sysName;
            }
        }
    }
}