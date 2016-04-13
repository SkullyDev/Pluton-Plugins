using System;
using System.IO;
using System.Collections.Generic;
using System.Runtime.Serialization.Formatters.Binary;
using UnityEngine;
using Pluton.Core;
using Pluton.Rust;
using Pluton.Rust.Events;
using Pluton.Rust.Objects;
using Pluton.Core.Serialize;
using Pluton.Rust.PluginLoaders;

namespace BuildingPartOwner
{
    public class BuildingPartOwner : CSharpPlugin
    {
        private List<SerializedBuildingBlock> OwnedBuildingBlocks;

        public void On_PluginInit()
        {
            Author = "SkullyDev";
            Version = "1.0";
            About = "";

            if (Server.Instance.Loaded) LoadSave();
        }

        public void On_ServerInit() { LoadSave(); }

        public void On_ServerShutdown() { SaveAll(); }

        public void On_PluginDeinit() { SaveAll(); }

        public void On_ServerSaved() { SaveAll(); }

        public void On_Placement(BuildingEvent be)
        {
            var newSeralized = new SerializedBuildingBlock(be.BuildingPart.buildingBlock, be.Builder.GameID);
            OwnedBuildingBlocks.Add(newSeralized);
        }

        public void On_NetworkableKill(BaseNetworkable bn)

        {
            var bb = bn.GetComponent<BuildingBlock>();
            if (bb != null) RemoveFromDB(bb);
        }

        private void LoadSave()
        {
            
            string path = Path.Combine(Util.GetPluginsFolder(), "BuildingPartOwner\\BuildingBlocks.bbsv");
            OwnedBuildingBlocks = new List<SerializedBuildingBlock>();
            if (!File.Exists(path)) return;
            try
            {
                var file = new FileInfo(path);
                using (var stream = new FileStream(file.FullName, FileMode.Open))
                {
                    var formatter = new BinaryFormatter();
                    OwnedBuildingBlocks = (List<SerializedBuildingBlock>)formatter.Deserialize(stream);
                }
            }
            catch
            {
                Debug.LogError("[BuildingPartOwner] Saved data can't be loaded because it is outdated!");
                Debug.LogError("[BuildingPartOwner] Version of file and plugin doesn't match!");
                Debug.LogError("[BuildingPartOwner] [OPTIONAL] Recommended wipe to have owners!");
            }
        }

        private void SaveAll()
        {
            string path = Path.Combine(Util.GetPluginsFolder(), "BuildingPartOwner\\BuildingBlocks.bbsv");
            using (var stream = new FileStream(path, FileMode.Create))
            {
                var formatter = new BinaryFormatter();
                formatter.Serialize(stream, OwnedBuildingBlocks);
            }
        }

        public bool RemoveFromDB(BuildingBlock bb)
        {
            if (bb == null) return false;
            foreach (var sbb in OwnedBuildingBlocks)
            {
                if (sbb.AreEqual(bb))
                {
                    OwnedBuildingBlocks.Remove(sbb);
                    return true;
                }
            }
            return false;
        }

        public string GetOwner(BuildingBlock bb)
        {
            if (bb != null)
            {
                foreach (var sbb in OwnedBuildingBlocks)
                {
                    if (sbb.AreEqual(bb))
                    {
                        return sbb.ownerID.ToString();
                    }
                }
            }
            return null;
        }

        public BuildingPart[] GetOwnedBuildingParts(ulong steamID)
        {
            if (steamID < 70000000000000000uL) return null;
            BuildingBlock[] bBlocks = UnityEngine.Object.FindObjectsOfType<BuildingBlock>();
            List<BuildingPart> BlockList = new List<BuildingPart>();
            foreach (var sbb in OwnedBuildingBlocks)
            {
                foreach (var bb in bBlocks)
                {
                    if (sbb.AreEqual(bb))
                    {
                        if (sbb.ownerID == steamID)
                        {
                            BlockList.Add(new BuildingPart(bb));
                        }
                        break;
                    }
                }
            }
            return BlockList.ToArray();
        }

        public bool IsOwner(BuildingBlock bb, ulong steamID)
        {
            if (steamID >= 70000000000000000uL && bb != null)
            {
                foreach (var sbb in OwnedBuildingBlocks)
                {
                    if (sbb.AreEqual(bb))
                    {
                        if (sbb.ownerID == steamID)
                        {
                            return true;
                        }
                    }
                }
            }
            return false;
        }
    }

    [Serializable]
    internal class SerializedBuildingBlock
    {
        internal ulong ownerID;
        internal string prefabName;
        internal SerializedVector3 pos;
        internal SerializedQuaternion rot;

        internal SerializedBuildingBlock(BuildingBlock bb, ulong owner)
        {
            ownerID = owner;
            prefabName = bb.LookupPrefabName();
            pos = new SerializedVector3(bb.transform.position);
            rot = new SerializedQuaternion(bb.transform.rotation);
        }

        internal bool AreEqual(BuildingBlock bb)
        {
            if (prefabName == bb.LookupPrefabName())
            {
                if (pos.ToVector3() == bb.transform.position)
                {
                    if (rot.ToQuaternion() == bb.transform.rotation)
                    {
                        return true;
                    }
                }
            }
            return false;
        }
    }
}