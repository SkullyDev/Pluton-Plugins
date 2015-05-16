using System;
using System.Collections.Generic;
using Pluton;
using UnityEngine;

namespace Dropper
{
    public class Dropper : CSharpPlugin
    {
        public class DropperPlane : MonoBehaviour
        {
            public int dropCountIn = 1;
            public bool[] dropped;
            public int dropCountTotal;
            public Vector3 lookAt;
            public Vector3 startPos;
            public Vector3[] dropPoints;
            public BaseEntity plane;
            public float wsize = global::World.Size;

            void Update()
            {
                if (!dropped[dropCountIn] && Vector3.Distance(this.transform.position, dropPoints[dropCountIn]) <= 1f)
                {
                    BaseEntity baseEntity = GameManager.server.CreateEntity("items/supply_drop", this.transform.position);
                    baseEntity.globalBroadcast = true;
                    baseEntity.Spawn();
                    dropped[dropCountIn] = true;
                    if (dropped[dropCountTotal])
                    {
                        lookAt = startPos;
                    }
                    else
                    {
                        dropCountIn++;
                        lookAt = dropPoints[dropCountIn];
                    }
                    
                }
                else if (!dropped[dropCountIn] && Vector3.Distance(this.transform.position, dropPoints[dropCountIn]) <= 100f)
                {
                    this.transform.LookAt(dropPoints[dropCountIn], new Vector3(0, this.transform.position.y, 0));
                }
                Quaternion rotatePoint = Quaternion.LookRotation(lookAt - this.transform.position);
                Quaternion slowly = Quaternion.Slerp(this.transform.rotation, rotatePoint, 0.3f * Time.deltaTime);
                this.transform.rotation = slowly;
                Vector3 forward = this.transform.position + this.transform.forward;
                forward.y = this.transform.position.y;
                this.transform.position = Vector3.MoveTowards(this.transform.position, forward, 50f * Time.deltaTime);
                plane.TransformChanged();
                if (dropped[dropCountTotal] && (this.transform.position.x >= wsize || this.transform.position.z >= wsize || this.transform.position.x <= -wsize || this.transform.position.z <= -wsize))
                {
                    this.SendMessage("KillMessage", 1);
                }
            }
        }

        private IniParser DropperIniSettings()
        {
            if (!Plugin.IniExists("DropperSettings"))
            {
                IniParser ini = Plugin.CreateIni("DropperSettings");
                ini.AddSetting("Settings", "Enabled", "1");
                ini.AddSetting("Settings", "EventEveryMins", "30");
                ini.AddSetting("Settings", "PlayersNeeded", "5");
                ini.AddSetting("Settings", "PlanesInSameTime", "1");
                ini.AddSetting("Settings", "DropsFromOnePlane", "1");
                ini.AddSetting("Settings", "BroadcastMsgName", "Dropper");
                ini.AddSetting("Settings", "BroadcastMsgLowPlayers", "AIRDROP WAS CANCELLED, NEED MORE PLAYER");
                ini.AddSetting("Settings", "BroadcastMsgAirdropIncoming", "AIRDROP CARGO PLANE INCOMING");
                ini.Save();
            }
            return Plugin.GetIni("DropperSettings");
        }

        public void On_ServerInit()
        {
            EventSchedule[] eventschedule = UnityEngine.Object.FindObjectsOfType<EventSchedule>();
            foreach (EventSchedule each in eventschedule) each.CancelInvoke("RunSchedule");
        }

        public void On_PluginInit()
        {
            ServerConsoleCommands.Register("airdrop").setCallback(SpawnPlaneCMD);
            ServerConsoleCommands.Register("plane").setCallback(SpawnPlaneCMD);
            EventSchedule[] eventschedule = UnityEngine.Object.FindObjectsOfType<EventSchedule>();
            foreach (EventSchedule each in eventschedule) each.CancelInvoke("RunSchedule");
            IniParser ini = DropperIniSettings();
            if (ini.GetSetting("Settings", "Enabled") == "1")
            {
                int mins = int.Parse(ini.GetSetting("Settings", "EventEveryMins"));
                int timer = mins * 60000;
                Plugin.CreateTimer("Drop", timer).Start();
            }
        }

        public void DropCallback(TimedEvent timer)
        {
            IniParser ini = DropperIniSettings();
            int online = Server.Players.Count;
            int needed = int.Parse(ini.GetSetting("Settings", "PlayersNeeded"));
            string sysName = ini.GetSetting("Settings", "BroadcastMsgName");
            if (online >= needed)
            {
                int drops = int.Parse(ini.GetSetting("Settings", "DropsFromOnePlane"));
                int planes = int.Parse(ini.GetSetting("Settings", "PlanesInSameTime"));
                for (int i = 1; i <= planes; i++) SpawnPlane(drops);
                string message = ini.GetSetting("Settings", "BroadcastMsgAirdropIncoming");
                Server.BroadcastFrom(sysName, message);
                Logger.Log("[EVENT] AIRDROP CARGO PLANE IN SERVER");
            }
            else
            {
                string message = ini.GetSetting("Settings", "BroadcastMsgLowPlayers");
                Server.BroadcastFrom(sysName, message);
            }
        }

        public void SpawnPlaneCMD(string[] cmd)
        {
            SpawnPlane(1);
            Logger.Log("[EVENT] AIRDROP CARGO PLANE IN SERVER");
        }

        public void SpawnPlane(int drops)
        {
            float worldsize = global::World.Size;
            float y = 1000f;
            Vector3 startingpos = default(Vector3);
            float pos = UnityEngine.Random.Range(-(worldsize / 3), worldsize / 3);
            int rand = UnityEngine.Random.Range(1, 100);
            int rand2 = UnityEngine.Random.Range(1, 100);
            if (rand >= 50)
            {
                startingpos.x = pos;
                if (rand2 <= 50)
                {
                    startingpos.z = worldsize;
                }
                else
                {
                    startingpos.z = -(worldsize);
                }
            }
            else
            {
                startingpos.z = pos;
                if (rand2 <= 50) startingpos.x = worldsize; else startingpos.x = -(worldsize);
            }
            startingpos.y = y;
            Vector3[] droppingpoint = new Vector3[drops + 1];
            for (int i = 1; i <= drops; i++)
            {
                bool grounded = false;
                while (!grounded)
                {
                    RaycastHit hit;
                    float x = UnityEngine.Random.Range(-worldsize, worldsize);
                    float z = UnityEngine.Random.Range(-worldsize, worldsize);
                    var origin = new Vector3(x, 1000f, z);
                    if (Physics.Raycast(origin, Vector3.down, out hit, 1100f, 1 << 23))
                    {
                        if (hit.point.y > 0f)
                        {
                            grounded = true;
                            droppingpoint[i].x = x;
                            droppingpoint[i].y = y;
                            droppingpoint[i].z = z;
                        }
                    }
                }
            }
            BaseEntity baseEntity = GameManager.server.CreateEntity("events/cargo_plane", startingpos, Quaternion.LookRotation(droppingpoint[1]));
            baseEntity.Spawn();
            CargoPlane[] cp = baseEntity.GetComponents<CargoPlane>();
            foreach (CargoPlane each in cp)
            {
                each.enabled = false;
            }
            baseEntity.transform.position = startingpos;
            baseEntity.transform.LookAt(droppingpoint[1], new Vector3(0,y,0));
            baseEntity.TransformChanged();
            DropperPlane classy = baseEntity.gameObject.AddComponent<DropperPlane>();
            classy.dropPoints = new Vector3[drops + 1];
            classy.dropped = new bool[drops + 1];
            classy.dropPoints = droppingpoint;
            classy.lookAt = droppingpoint[1];
            classy.dropCountTotal = drops;
            classy.startPos = startingpos;
            classy.plane = baseEntity;
        }
    }
}