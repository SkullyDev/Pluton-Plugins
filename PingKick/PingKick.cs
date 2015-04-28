using Pluton;

namespace PingKick
{
    public class PingKick : CSharpPlugin
    {
        public IniParser SettingsIni()
        {
            if (!Plugin.IniExists("Settings"))
            {
                IniParser ini = Plugin.CreateIni("Settings");
                ini.AddSetting("Settings","MaxPing", "400");
                ini.AddSetting("Settings", "CheckSeconds", "60");
                ini.AddSetting("Settings", "KickMessage", "Your ping is too high");
                ini.Save();
            }
            return Plugin.GetIni("Settings");
        }

        public void On_PluginInit()
        {
            IniParser ini = SettingsIni();
            string kickMsg = ini.GetSetting("Settings", "KickMessage");
            int maxPing = int.Parse(ini.GetSetting("Settings", "MaxPing"));
            int checkSec = int.Parse(ini.GetSetting("Settings", "CheckSeconds")) * 1000;
            DataStore.Add("PingCheck", "MaxPing", maxPing);
            DataStore.Add("PingCheck", "KickMSG", kickMsg);
            Plugin.CreateTimer("CheckPlayerPing", checkSec).Start();
        }

        public void CheckPlayerPingCallback(TimedEvent timer)
        {
            int maxPing = (int)DataStore.Get("PingCheck", "MaxPing");
            string kickMsg = (string)DataStore.Get("PingCheck", "KickMSG");
            foreach(Player player in Server.ActivePlayers)
            {
                if (Network.Net.sv.GetAveragePing(player.basePlayer.net.connection) > maxPing)
                {
                    player.Kick(kickMsg + " (" + Network.Net.sv.GetAveragePing(player.basePlayer.net.connection).ToString() + ")");
                }
            }
        }
    }
}