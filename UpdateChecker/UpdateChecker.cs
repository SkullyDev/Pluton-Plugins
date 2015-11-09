using System;
using System.Linq;
using System.Collections.Generic;
using Pluton;
using SimpleJSON;

namespace UpdateChecker
{
    public class UpdateChecker : CSharpPlugin
    {
        string lastJson = string.Empty;
        DateTime lastChange = DateTime.Now;
        List<string> oldPluginNames = new List<string>();

        public void On_PluginInit()
        {
            Author = "SkullyDev";
            Version = "0.5";
            About = "Checks all plugin versions and notifies administrators if there is an update available";
            Plugin.CreateTimer("CheckPlugVers", 5000).Start();
        }

        public void CheckPlugVersCallback(TimedEvent timer)
        {
            if (!Server.Loaded) return;
            var webClient = new System.Net.WebClient();
            webClient.Encoding = System.Text.Encoding.UTF8;
            string json = webClient.DownloadString("http://stats.pluton-team.org/all_plugins.php");
            var plugins = PluginLoader.GetInstance().Plugins.Values.ToList();
            var newPluginNames = plugins.Select(x => x.Name).ToList();
            if (json == lastJson && lastChange.AddHours(1d) > DateTime.Now && newPluginNames == oldPluginNames) return;
            lastJson = json;
            lastChange = DateTime.Now;
            var data = JSON.Parse(json);
            oldPluginNames = new List<string>();
            foreach (BasePlugin plugin in plugins)
            {
                oldPluginNames.Add(plugin.Name);
                foreach (JSONNode resource in data["resources"].AsArray)
                {
                    string name = resource["title"].Value;
                    string author = resource["author_username"].Value;
                    string version = resource["version_string"].Value;
                    //Logger.LogWarning("Name: " + name);
                    //Logger.LogWarning("Author: " + author);
                    //Logger.LogWarning("Version: " + version);
                    if (name == plugin.Name && author == plugin.Author)
                    {
                        if (version == plugin.Version) break;
                        string msg = string.Format("New version for plugin {0} available on Pluton forum!", name);
                        Logger.LogWarning(msg);
                        foreach (Player player in Server.ActivePlayers)
                        {
                            if (!player.Admin) continue;
                            player.MessageFrom("UpdateChecker", msg);
                        }
                    }
                }
            }
        }
    }
}