using System;
using System.Timers;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using Rust;
using Pluton;
using Pluton.Events;
using UnityEngine;

namespace ColoredChat
{
    public class ColoredChat : CSharpPlugin
    {
        Dictionary<string, string> colorCodes;
        Dictionary<string, string> colorCodesAdmin;

        public void On_PluginInit()
        {
            DataStore.Flush("ColoredChat");
            Commands.Register("ccolor").setCallback(ColorCommand);

            colorCodes = new Dictionary<string, string>();
            colorCodes.Add("red", "FF0000");
            colorCodes.Add("blue", "1F45FC");
            colorCodes.Add("purple", "800080");
            colorCodes.Add("yellow", "FFFF00");
            colorCodes.Add("pink", "F660AB");
            colorCodes.Add("orange", "FFA500");
            colorCodes.Add("green", "008000");
            colorCodes.Add("teal", "008080");
            colorCodes.Add("lime", "5EFB6E");
            colorCodes.Add("brown", "A52A2A");
            colorCodes.Add("silver", "C0C0C0");
            colorCodes.Add("maroon", "800000");
            colorCodes.Add("olive", "808000");

            colorCodesAdmin = new Dictionary<string, string>();
            colorCodesAdmin.Add("black", "000000");
            colorCodesAdmin.Add("hpink", "FAAFBE");
            colorCodesAdmin.Add("npink", "F433FF");
            colorCodesAdmin.Add("dgreen", "6AFB92");
            colorCodesAdmin.Add("jgreen", "00FF00");
            colorCodesAdmin.Add("cyan", "00FFFF");
            colorCodesAdmin.Add("sblue", "736AFF");
        }

        public void ColorCommand(string[] args, Player player)
        {
            if (args.Length > 0 && args[0] != "")
            {
                string color = args[0].ToLower();
                if (colorCodes.ContainsKey(color))
                {
                    DataStore.Add("ColoredChat", player.GameID, color);
                    player.Message("<color=#" + colorCodes[color] + ">This is your new chat color</color>");
                }
                else if (player.Admin && colorCodesAdmin.ContainsKey(color))
                {
                    DataStore.Add("ColoredChat", player.GameID, color);
                    player.Message("<color=#" + colorCodesAdmin[color] + ">This is your new chat color</color>");
                }
                else
                {
                    player.Message("Given color name was not found!");
                }
            }
            else
            {
                if (DataStore.ContainsKey("ColoredChat", player.GameID))
                {
                    DataStore.Remove("ColoredChat", player.GameID);
                    player.Message("Your chat color was set to default!");
                    return;
                }
                player.Message("USAGE: /color red");
                player.Message("Usable colors: "
                    + "<color=#FF0000>Red</color>, "
                    + "<color=#1F45FC>Blue</color>, "
                    + "<color=#800080>Purple</color>, "
                    + "<color=#FFFF00>Yellow</color>, "
                    + "<color=#F660AB>Pink</color>, "
                    + "<color=#FFA500>Orange</color>, "
                    + "<color=#008000>Green</color>, "
                    + "<color=#008080>Teal</color>, "
                    + "<color=#5EFB6E>Lime</color>, "
                    + "<color=#A52A2A>Brown</color>, "
                    + "<color=#C0C0C0>Silver</color>, "
                    + "<color=#800000>Maroon</color>, "
                    + "<color=#808000>Olive</color>"
                );
                if (player.Admin)
                {
                    player.Message("Admin Colors: "
                        + "<color=#000000>Black</color>, "
                        + "<color=#FAAFBE>HPink</color>, "
                        + "<color=#F433FF>NPink</color>, "
                        + "<color=#6AFB92>DGreen</color>, "
                        + "<color=#00FF00>JGreen</color>, "
                        + "<color=#00FFFF>Cyan</color>, "
                        + "<color=#736AFF>SBlue</color>"
                    );
                }
            }
        }

        public void On_Chat(ChatEvent ce)
        {
            Player player = ce.User;
            if (DataStore.ContainsKey("ColoredChat", player.GameID))
            {
                string colorCode;
                if (player.Admin)
                {
                    colorCode = colorCodesAdmin[(string)DataStore.Get("ColoredChat", player.GameID)];
                }
                else
                {
                    colorCode = colorCodes[(string)DataStore.Get("ColoredChat", player.GameID)];
                }
                ce.FinalText = string.Format("<color=#{0}>{1}</color>", colorCode, ce.FinalText);
            }
        }
    }
}