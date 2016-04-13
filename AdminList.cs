using System;
using UnityEngine;
using Pluton.Core;
using Pluton.Rust;
using Pluton.Rust.Events;
using Pluton.Rust.Objects;
using Pluton.Rust.PluginLoaders;

namespace AdminList
{
    public class AdminList: CSharpPlugin
    {
        public void On_PluginInit()
        {
            Author = "SkullyDev";
            Version = "1.0";
            About = "";

            Commands.Register("admins").setCallback(AdminsCommand);
        }

        public void AdminsCommand(string[] args, Player player)
        {
            string nameList = string.Empty;
            foreach (Player pl in Server.Instance.ActivePlayers) {
                if (pl.Admin) nameList = nameList + pl.Name + ", ";
            }
            if (nameList == "") player.Message("Sorry but there are no admins online at this moment");
            else player.Message("ADMINS: " + nameList.Remove(nameList.Length - 2));
        }
    }
}