using System;
using System.Collections.Generic;
using Pluton;
using UnityEngine;

namespace Droper
{
    public class Droper : CSharpPlugin
    {
        public class DroperPlane : MonoBehaviour
        {
            bool dropped = false;
            public float wsize = global::World.Size;
            public Vector3 dropPoint;
            public BaseEntity plane;

            void Update()
            {
                if (!dropped && Vector3.Distance(dropPoint, this.transform.position) <= 1f)
                {
                    BaseEntity baseEntity = GameManager.server.CreateEntity("items/supply_drop", this.transform.position);
                    baseEntity.globalBroadcast = true;
                    baseEntity.Spawn();
                    dropped = true;
                    //Logger.LogDebug("DROP SPAWNED");
                }
                Vector3 forward = this.transform.position + this.transform.forward;
                forward.y = this.transform.position.y;
                this.transform.position = Vector3.MoveTowards(this.transform.position, forward, 100f * Time.deltaTime);
                plane.TransformChanged();
                if (this.transform.position.x >= wsize || this.transform.position.z >= wsize || this.transform.position.x <= -wsize || this.transform.position.z <= -wsize)
                {
                    this.SendMessage("KillMessage", 1);
                    //Logger.LogDebug("PLANE KILLED");
                }
            }
        }

        private IniParser DroperIniSettings()
        {
            if (!Plugin.IniExists("DroperSettings"))
            {
                IniParser ini = Plugin.CreateIni("DroperSettings");
                ini.AddSetting("Settings", "Enabled", "1");
                ini.AddSetting("Settings", "EventEveryMins", "30");
                ini.AddSetting("Settings", "PlayersNeeded", "5");
                ini.AddSetting("Settings", "PlanesInSameTime", "1");
                ini.AddSetting("Settings", "BroadcastMsgName", "Droper");
                ini.AddSetting("Settings", "BroadcastMsgLowPlayers", "AIRDROP WAS CANCELLED, NEED MORE PLAYER");
                ini.AddSetting("Settings", "BroadcastMsgAirdropIncoming", "AIRDROP CARGO PLANE INCOMING");
                ini.Save();
            }
            return Plugin.GetIni("DroperSettings");
        }
        public void On_ServerInit()
        {
            EventSchedule[] eventschedule = UnityEngine.Object.FindObjectsOfType<EventSchedule>();
            foreach (EventSchedule each in eventschedule) each.CancelInvoke("RunSchedule");
        //}

        //public void On_PluginInit()
        //{
        //    EventSchedule[] eventschedule = UnityEngine.Object.FindObjectsOfType<EventSchedule>();
        //    foreach (EventSchedule each in eventschedule) each.CancelInvoke("RunSchedule");
            ServerConsoleCommands.Register("plane").setCallback("SpawnPlane");
            IniParser ini = DroperIniSettings();
            if (ini.GetSetting("Settings", "Enabled") == "1")
            {
                int mins = int.Parse(ini.GetSetting("Settings", "EventEveryMins"));
                int timer = mins * 60000;
                Plugin.CreateTimer("Drop", timer).Start();
            }
        }

        public void DropCallback(TimedEvent timer)
        {
            IniParser ini = DroperIniSettings();
            int online = Server.Players.Count;
            int needed = int.Parse(ini.GetSetting("Settings", "PlayersNeeded"));
            string sysName = ini.GetSetting("Settings", "BroadcastMsgName");
            if (online >= needed)
            {
                int planes = int.Parse(ini.GetSetting("Settings", "PlanesInSameTime"));
                for (int i = 0; i < planes; i++)
                {
                    //Logger.LogDebug("SPAWNING PLANE");
                    SpawnPlane();
                    i = i + 1;
                }
                string message = ini.GetSetting("Settings", "BroadcastMsgAirdropIncoming");
                Server.BroadcastFrom(sysName, message);
            }
            else
            {
                string message = ini.GetSetting("Settings", "BroadcastMsgLowPlayers");
                Server.BroadcastFrom(sysName, message);
            }
        }

        public void SpawnPlane()
        {
            bool grounded = false;
            float worldsize = global::World.Size;
            float y = global::World.HighestPoint.y + 500f;
            Vector3 startingpos;
            Vector3 droppingpoint;
            float x = 50f;
            float z = 50f;
            while (!grounded)
            {
                RaycastHit hit;
                x = UnityEngine.Random.Range(-worldsize, worldsize);
                z = UnityEngine.Random.Range(-worldsize, worldsize);
                var origin = new Vector3(x, global::World.HighestPoint.y + 1f, z);
                if (Physics.Raycast(origin, Vector3.down, out hit, global::World.HighestPoint.y + 101f, 1 << 23))
                {
                    if (hit.point.y > 0f) grounded = true;
                    //else Logger.LogDebug("REGENERATING DROP POINT");
                }
            }
            droppingpoint.x = x;
            droppingpoint.y = y;
            droppingpoint.z = z;
            float pos = UnityEngine.Random.Range(-(worldsize / 3), worldsize / 3);
            int rand = UnityEngine.Random.Range(1, 100);
            int rand2 = UnityEngine.Random.Range(1, 100);
            if (rand >= 50)
            {
                startingpos.x = pos;
                if (rand2 <= 50) startingpos.z = worldsize; else startingpos.z = -(worldsize);
            }
            else
            {
                startingpos.z = pos;
                if (rand2 <= 50) startingpos.x = worldsize; else startingpos.x = -(worldsize);
            }
            startingpos.y = y;
            BaseEntity baseEntity = GameManager.server.CreateEntity("events/cargo_plane", startingpos, Quaternion.LookRotation(droppingpoint));
            baseEntity.Spawn();
            CargoPlane[] cp = baseEntity.GetComponents<CargoPlane>();
            foreach (CargoPlane each in cp) each.enabled = false;
            baseEntity.transform.position = startingpos;
            baseEntity.transform.LookAt(droppingpoint, new Vector3(0,y,0));
            baseEntity.TransformChanged();
            DroperPlane classy = baseEntity.gameObject.AddComponent<DroperPlane>();
            classy.dropPoint = droppingpoint;
            classy.plane = baseEntity;
        }
    }
}