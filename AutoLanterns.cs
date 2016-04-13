using System;
using UnityEngine;
using Pluton.Core;
using Pluton.Rust;
using Pluton.Rust.Events;
using Pluton.Rust.Objects;
using Pluton.Rust.PluginLoaders;

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

        public void On_PluginInit()
        {
            Author = "SkullyDev";
            Version = "1.0";
            About = "";

            if (!Server.Instance.Loaded) return;
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

        public void On_ServerInit()
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
            float timeNow = TOD_Sky.Instance.Cycle.Hour;
            if ((timeNow >= (float)DataStore.Get("AutoLanterns", "TurnOnTime") || timeNow <= (float)DataStore.Get("AutoLanterns", "TurnOffTime")) && !(bool)DataStore.Get("AutoLanterns", "Turned"))
            {
                foreach (BaseOven baseOven in Component.FindObjectsOfType<BaseOven>()) if (baseOven.name.Contains("lantern")) baseOven.Invoke("StartCooking", 1f);
                DataStore.Add("AutoLanterns", "Turned", true);
            } else if (timeNow <= (float)DataStore.Get("AutoLanterns", "TurnOnTime") && timeNow >= (float)DataStore.Get("AutoLanterns", "TurnOffTime") && (bool)DataStore.Get("AutoLanterns", "Turned")) {
                foreach (BaseOven baseOven in Component.FindObjectsOfType<BaseOven>()) if (baseOven.name.Contains("lantern")) baseOven.Invoke("StopCooking", 1f);
                DataStore.Add("AutoLanterns", "Turned", false);
            }
        }
    }
}