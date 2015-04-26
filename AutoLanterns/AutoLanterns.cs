using System;
using Pluton;
using UnityEngine;

namespace AutoLanterns
{
    public class AutoLanterns : CSharpPlugin
    {
        private IniParser IniSettings()
        {
            if (!Plugin.IniExists("DroperSettings"))
            {
                IniParser ini = Plugin.CreateIni("Settings");
                ini.AddSetting("Settings", "Enabled", "1");
                ini.AddSetting("Settings", "CheckEverySec", "3");
                ini.AddSetting("Settings", "TurnOnTime", "17.5");
                ini.AddSetting("Settings", "TurnOffTime", "5.5");
                ini.Save();
            }
            return Plugin.GetIni("Settings");
        }

        //public void On_ServerInit()
        public void On_PluginInit()
        {
            IniParser ini = IniSettings();
            if (ini.GetSetting("Settings", "Enabled") == "1")
            {
                DataStore.Add("AutoLanterns", "Turned", false);
                DataStore.Add("AutoLanterns", "TurnOnTime", float.Parse(ini.GetSetting("Settings", "TurnOnTime")));
                DataStore.Add("AutoLanterns", "TurnOffTime", float.Parse(ini.GetSetting("Settings", "TurnOffTime")));
                int secs = int.Parse(ini.GetSetting("Settings", "CheckEverySec"));
                int timer = secs * 1000;
                Plugin.CreateTimer("CheckLanterns", timer).Start();
            }
        }

        public void CheckLanternsCallback(TimedEvent timer)
        {
            if ((World.Time >= (float)DataStore.Get("AutoLanterns", "TurnOnTime") || World.Time <= (float)DataStore.Get("AutoLanterns", "TurnOffTime")) && !(bool)DataStore.Get("AutoLanterns", "Turned"))
            {
                foreach (BaseEntity worldObject in UnityEngine.Object.FindObjectsOfType<BaseEntity>())
                {
                    if (worldObject.name.Contains("lantern"))
                    {
                        BaseOven baseOven = worldObject.GetComponent<BaseOven>();
                        baseOven.Invoke("StartCooking", 1f);
                    }
                }
                DataStore.Add("AutoLanterns", "Turned", true);
            }
            else if (World.Time <= (float)DataStore.Get("AutoLanterns", "TurnOnTime") && World.Time >= (float)DataStore.Get("AutoLanterns", "TurnOffTime") && (bool)DataStore.Get("AutoLanterns", "Turned"))
            {
                foreach (BaseEntity worldObject in UnityEngine.Object.FindObjectsOfType<BaseEntity>())
                {
                    if (worldObject.name.Contains("lantern"))
                    {
                        BaseOven baseOven = worldObject.GetComponent<BaseOven>();
                        baseOven.Invoke("StopCooking", 1f);
                    }
                }
                DataStore.Add("AutoLanterns", "Turned", false);
            }
        }
    }
}