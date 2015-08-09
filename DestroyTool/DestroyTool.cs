using System;
using System.Collections.Generic;
using Pluton;
using UnityEngine;

namespace DestroyTool
{
    public class DestroyTool : CSharpPlugin
    {
        int layerMasks = LayerMask.GetMask("Construction", "Construction Trigger", "Deployed");

        public void On_PluginInit()
        {
            Commands.Register("destroy").setCallback(DestroyCommand);
            DataStore.Flush("DestroyTool");
            DataStore.Flush("DestroyAdmin");
            DataStore.Flush("DestroyAll");
        }
        
        public void DestroyCommand(string[] args, Player player)
        {
            if (DataStore.ContainsKey("DestroyTool", player.GameID))
            {
                foreach (TimedEvent timer in Plugin.GetParallelTimer("DestroyRemove"))
                {
                    if ((ulong)timer.Args["SteamID"] == player.GameID)
                    {
                        timer.Kill();
                        break;
                    }
                }
                DataStore.Remove("DestroyTool", player.GameID);
                player.Message("Destroy tool was deactivated");
            }
            else if (DataStore.ContainsKey("DestroyAdmin", player.GameID))
            {
                DataStore.Remove("DestroyAdmin", player.GameID);
                player.Message("Destroy tool \"admin\" was deactivated");
            }
            else if (DataStore.ContainsKey("DestroyAll", player.GameID))
            {
                DataStore.Remove("DestroyAll", player.GameID);
                player.Message("Destroy tool \"all\" was deactivated");
            }
            else if (args.Length > 0 && player.Admin)
            {
                if (args[0] == "admin")
                {
                    DataStore.Add("DestroyAdmin", player.GameID, true);
                    player.Message("Destroy tool \"admin\" was activated");
                    player.Message("Don't forget to turn it off with: /destroy");
                }
                else if (args[0] == "all")
                {
                    DataStore.Add("DestroyAll", player.GameID, true);
                    player.Message("Destroy tool \"all\" was activated");
                    player.Message("Don't forget to turn it off with: /destroy");
                }
            }
            else
            {
                DataStore.Add("DestroyTool", player.GameID, true);
                Dictionary<string, object> timerDict = new Dictionary<string, object>();
                timerDict["SteamID"] = player.GameID;
                Plugin.CreateParallelTimer("DestroyRemove", 60000, timerDict).Start();
                player.Message("Destory tool was activated for 60 seconds");
            }
        }

        public void On_CombatEntityHurt(Pluton.Events.CombatEntityHurtEvent cehe)
        {
            if (cehe.Attacker == null) return;
            Player player = cehe.Attacker.ToPlayer();
            if (player != null)
            {
                if (DataStore.ContainsKey("DestroyTool", player.GameID))
                {
                    if (Vector3.Distance(cehe.Victim.Location, player.Location) <= 4f)
                    {
                        BasePlugin basePlugin = Plugin.GetPlugin("BuildingPartOwner");
                        var bce = cehe.Victim.baseEntity.GetComponent<BaseCombatEntity>();
                        var bb = cehe.Victim.baseEntity.GetComponentInParent<BuildingBlock>();
                        if (basePlugin != null && bb != null)
                        {
                            if ((bool)basePlugin.Invoke("IsOwner", bb, player.GameID))
                            {
                                foreach (var ia in bb.currentGrade.costToBuild)
                                {
                                    player.Inventory.Add(ia.itemDef.shortname, (int)ia.amount);
                                }
                                bce.Die(cehe._info);
                            }
                            else
                            {
                                player.Message("You don't own this building part!");
                                return;
                            }
                        }
                        else
                        {
                            int hasPrivlidge = 0;
                            List<BuildingPrivlidge> cupboards = (List<BuildingPrivlidge>)player.basePlayer.GetFieldValue("buildingPrivlidges");
                            foreach (BuildingPrivlidge privlidge in cupboards) if (privlidge.IsAuthed(player.basePlayer)) hasPrivlidge++;
                            if (cupboards.Count == 0)
                            {
                                player.Message("Place a \"tool cupboard\" first");
                                return;
                            }
                            else if (hasPrivlidge < cupboards.Count)
                            {
                                player.Message("You do not have the privilege of building here");
                                return;
                            }
                            else
                            {
                                if (bb != null)
                                {
                                    foreach (var ia in bb.currentGrade.costToBuild)
                                    {
                                        player.Inventory.Add(ia.itemDef.shortname, (int)ia.amount);
                                    }
                                }
                                else
                                {
                                    string prefabName = cehe.Victim.baseEntity.LookupShortPrefabName();
                                    player.Inventory.Add(prefabName, 1);
                                }
                                bce.Die(cehe._info);
                            }
                        }
                    }
                }
                else if (DataStore.ContainsKey("DestroyAdmin", player.GameID))
                {
                     cehe.Victim.baseEntity.GetComponent<BaseCombatEntity>().Die(cehe._info);
                }
                else if (DataStore.ContainsKey("DestroyAll", player.GameID))
                {
                    cehe.Victim.baseEntity.GetComponentInParent<BaseCombatEntity>().Die(cehe._info);
                    List<Vector3> posList = new List<Vector3>();
                    posList.Add(cehe.Victim.Location);
                    for (int i = 0; i < posList.Count; i++)
                    {
                        Collider[] colliders = Physics.OverlapSphere(posList[i], 3f, layerMasks);
                        foreach (Collider collider in colliders)
                        {
                            if (collider.isTrigger) continue;
                            if (!posList.Contains(collider.transform.position))
                            {
                                var bce = collider.GetComponentInParent<BaseCombatEntity>();
                                posList.Add(bce.transform.position);
                                if (bce != null) bce.Die(cehe._info);
                            }
                        }
                    }
                }
            }
        }

        public void DestroySurrounding(Vector3 startPos, HitInfo info)
        {
            Collider[] colliders = Physics.OverlapSphere(startPos, 3f, layerMasks);
            foreach (Collider collider in colliders)
            {
                if (collider.isTrigger) continue;
                var bce = collider.GetComponentInParent<BaseCombatEntity>();
                if (bce != null) bce.Die(info);

            }
        }

        public void DestroyRemoveCallback(TimedEvent timer)
        {
            ulong steamID = (ulong)timer.Args["SteamID"];
            if (DataStore.ContainsKey("DestroyTool", steamID))
            {
                DataStore.Remove("DestroyTool", steamID);
                Player player = Server.Players[steamID];
                if (player != null) player.Message("Destroy tool was deactivated");
                timer.Kill();
            }
        }
    }
}