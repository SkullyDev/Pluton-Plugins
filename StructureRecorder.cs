using System;
using System.IO;
using System.Linq;
using System.Collections;
using System.Collections.Generic;
using System.Runtime.Serialization.Formatters.Binary;
using UnityEngine;
using Pluton.Core;
using Pluton.Rust;
using Pluton.Rust.Events;
using Pluton.Rust.Objects;
using Pluton.Core.Serialize;
using Pluton.Rust.PluginLoaders;

namespace StructureRecorder
{
    public class StructureRecorder : CSharpPlugin
    {
        public Dictionary<string, Structure> Structures;

        public void On_Command(CommandEvent cmd)
        {
            try
            {
                Player player = cmd.User;
                string command = cmd.Cmd;
                string[] args = cmd.Args;
                if (command == "srstart")
                {
                    if (args.Length == 0 || (args.Length == 1 && args[0] == ""))
                    {
                        player.Message("USAGE: /srstart StructureName");
                        return;
                    }
                    if (DataStore.ContainsKey("StructureRecorder", player.SteamID))
                    {
                        player.Message("Recording is already running");
                        return;
                    }
                    string name = args[0];
                    StartRecording(name, player.SteamID);
                    player.Message("Recording was started on name \"" + name + "\"");
                }
                else if (command == "srstop")
                {
                    if (!DataStore.ContainsKey("StructureRecorder", player.SteamID))
                    {
                        player.Message("There is nothing to stop");
                        player.Message("Start one using: /srstart StructureName");
                        return;
                    }
                    string name = (string)DataStore.Get("StructureRecorder", player.SteamID);
                    DataStore.Remove("StructureRecorder", player.SteamID);
                    StopRecording(name);
                    player.Message("Recording was stopped");
                }
                else if (command == "srbuild")
                {
                    if (args.Length == 0 || (args.Length == 1 && args[0] == ""))
                    {
                        player.Message("USAGE: /srbuild StructureName");
                        return;
                    }
                    Structure structure;
                    Structures.TryGetValue(args[0], out structure);
                    if (structure == null)
                    {
                        player.Message("Building wasn't found by name \"" + args[0] + "\"");
                        return;
                    }
                    structure.Build(player.Location);
                    player.Message("Building was spawned");
                }
            }
            catch (Exception ex)
            {
                Pluton.Core.Logger.LogException(ex);
            }
        }

        public void On_PluginInit()
        {
            Author = "SkullyDev";
            Version = "1.0";
            About = "";

            DataStore.Flush("StructureRecorder");
            DataStore.Flush("StructureRecorderEveryone");
            if (!Server.Instance.Loaded) return;
            Structures = new Dictionary<string, Structure>();
            LoadStructures();
        }

        public void On_ServerInit()
        {
            Structures = new Dictionary<string, Structure>();
            LoadStructures();
        }

        public void On_CombatEntityHurt(CombatEntityHurtEvent cehe)
        {
            if (cehe.Attacker == null || cehe.Victim == null) return;
            Player player = cehe.Attacker.ToPlayer();
            BuildingPart bp = cehe.Victim.ToBuildingPart();
            if (player == null || bp == null) return;
            string name = ""; 
            if (DataStore.ContainsKey("StructureRecorder", player.SteamID))
            {
                name = (string)DataStore.Get("StructureRecorder", player.SteamID);
            }
            else if (DataStore.ContainsKey("StructureRecorderEveryone", "ON"))
            {
                name = (string)DataStore.Get("StructureRecorderEveryone", "ON");
            }
            else
            {
                return;
            }
            Structure structure;
            Structures.TryGetValue(name, out structure);
            if (structure == null) return;
            foreach (int dmg in Enumerable.Range(0, cehe.DamageAmounts.Length))
            {
                cehe.DamageAmounts[dmg] = 0f;
            }
            if (cehe.DamageType == Rust.DamageType.ElectricShock)
            {
                RecordAllConnected(structure, bp);
                player.Message("Added everything including connected parts");
                return;
            }
            structure.AddComponent(bp);
            player.Message("Added " + bp.Name);
        }

        public void On_Placement(BuildingEvent be)
        {
            Player player = be.Builder;
            string name = "";
            if (DataStore.ContainsKey("StructureRecorder", player.SteamID))
            {
                name = (string)DataStore.Get("StructureRecorder", player.SteamID);
            }
            else if (DataStore.ContainsKey("StructureRecorderEveryone", "ON"))
            {
                name = (string)DataStore.Get("StructureRecorderEveryone", "ON");
            }
            else
            {
                return;
            }
            BuildingPart bp = be.BuildingPart;
            Structure structure;
            Structures.TryGetValue(name, out structure);
            if (structure == null) return;
            structure.AddComponent(bp);
            player.Message("Added " + bp.Name);
        }

        public void StartRecording(string name, string steamID = "")
        {
            if (Structures.ContainsKey(name)) {
                Structures.Remove(name);
                if (File.Exists(name + ".sps")) File.Delete(name + ".sps");
            }
            if (steamID == "") DataStore.Add("StructureRecorderEveryone", "ON", name);
            else DataStore.Add("StructureRecorder", steamID, name);
            Structure structure = CreateStructure(name);
            Structures.Add(name, structure);
        }

        public void StopRecording(string name)
        {
            Structure structure;
            Structures.TryGetValue(name, out structure);
            DataStore.Remove("StructureRecorder", name);
            structure.Export();
        }

        public Structure CreateStructure(string name)
        {
            return new Structure(name);
        }

        public void LoadStructures()
        {
            DirectoryInfo structuresPath = new DirectoryInfo(Path.Combine(Plugin.GetPluginPath(), "StructureRecorder"));
            Structures.Clear();
            foreach (FileInfo file in structuresPath.GetFiles())
            {
                if (file.Extension.ToLower() == ".sps")
                {
                    using (FileStream stream = new FileStream(file.FullName, FileMode.Open))
                    {
                        BinaryFormatter formatter = new BinaryFormatter();
                        object thing = formatter.Deserialize(stream);
                        Structure structure = thing as Structure;
                        Structures.Add(file.Name.Substring(0, file.Name.Length - 5), structure);
                    }
                }
            }
        }

        private void RecordAllConnected(Structure structure, BuildingPart bp)
        {
            List<object> partList = new List<object>();
            List<Vector3> posList = new List<Vector3>();
            int layerMasks = LayerMask.GetMask("Construction", "Construction Trigger", "Deployed");
            partList.Add(bp.buildingBlock);
            posList.Add(bp.Location);
            structure.AddComponent(bp);
            for (int i = 0; i < posList.Count; i++)
            {
                Collider[] colliders = Physics.OverlapSphere(posList[i], 3f, layerMasks);
                foreach (Collider collider in colliders)
                {
                    if (collider.isTrigger) continue;
                    if (collider.GetComponentInParent<BuildingBlock>() != null)
                    {
                        BuildingBlock buildingBlock = collider.GetComponentInParent<BuildingBlock>();
                        if (!partList.Contains(buildingBlock))
                        {
                            partList.Add(buildingBlock);
                            posList.Add(buildingBlock.transform.position);
                            structure.AddComponent(new BuildingPart(buildingBlock));
                        }
                    }
                    else if (collider.GetComponentInParent<Deployable>() != null)
                    {
                        Deployable deployable = collider.GetComponentInParent<Deployable>();
                        if (!partList.Contains(deployable))
                        {
                            partList.Add(deployable);
                            posList.Add(deployable.transform.position);
                            structure.AddComponent(deployable);
                        }
                    }
                    else if (collider.GetComponentInParent<Spawnable>() != null)
                    {
                        Spawnable spawnable = collider.GetComponentInParent<Spawnable>();
                        if (!partList.Contains(spawnable))
                        {
                            partList.Add(spawnable);
                            posList.Add(spawnable.transform.position);
                            structure.AddComponent(spawnable);
                        }
                    }
                }
            }
        }
    }

    [Serializable]
    public class Origo : CountedInstance
    {
        public SerializedVector3 Position;
        public SerializedQuaternion Rotation;

        public Origo(SerializedVector3 v3, SerializedQuaternion q)
        {
            Position = v3;
            Rotation = q;
        }
    }

    [Serializable]
    public class StructureComponent : CountedInstance
    {
        public float Health;
        public string Prefab;
        public bool HasKeyLock;
        public bool HasCodeLock;
        public string LockCode;
        public List<ulong> LockWList;
        public BuildingGrade.Enum Grade;
        public SerializedVector3 LocalPosition;
        public SerializedQuaternion LocalRotation;

        public StructureComponent(BuildingPart bp, SerializedVector3 v3, SerializedQuaternion q)
        {
            Grade = bp.buildingBlock.grade;
            Prefab = bp.buildingBlock.LookupPrefabName();
            LocalPosition = v3;
            LocalRotation = q;
            Health = (float)((int)Math.Floor((double)(bp.Health / 85)) * 85);
            if (bp.buildingBlock.HasSlot(BaseEntity.Slot.Lock))
            {
                BaseLock baseLock = bp.buildingBlock.GetSlot(BaseEntity.Slot.Lock) as BaseLock;
                if (baseLock == null)
                {
                    HasCodeLock = false;
                    HasKeyLock = false;
                }
                else if (baseLock.GetComponent<CodeLock>())
                {
                    HasCodeLock = true;
                    HasKeyLock = false;
                    CodeLock codeLock = baseLock.GetComponent<CodeLock>();
                    if (!string.IsNullOrEmpty((string)codeLock.GetFieldValue("code")))
                    {
                        LockCode = (string)codeLock.GetFieldValue("code");
                        LockWList = new List<ulong>();
                        LockWList = (List<ulong>)codeLock.GetFieldValue("whitelistPlayers");
                    }
                }
                else if (baseLock.GetComponent<KeyLock>())
                {
                    HasCodeLock = false;
                    HasKeyLock = true;
                    KeyLock keyLock = baseLock.GetComponent<KeyLock>();
                    int keyCode = (int)keyLock.GetFieldValue("keyCode");
                    keyCode = (bool)keyLock.GetFieldValue("firstKeyCreated") ? keyCode |= 0x80 : (int)keyLock.GetFieldValue("keyCode");
                    LockCode = keyCode.ToString();
                }
            }
        }

        public override string ToString()
        {
            return String.Format("{0} [pos:{1}, rot:{2}]", Prefab, LocalPosition, LocalRotation);
        }
    }

    [Serializable]
    public class DeployableComponent : CountedInstance
    {
        public string BagName;
        public string Prefab;
        public bool IsCupBoard;
        public bool HasOwner;
        public bool HasKeyLock;
        public bool HasCodeLock;
        public bool HasStorage;
        public bool HasPainting;
        public ulong DeployedBy;
        public string LockCode;
        public byte[] Painting;
        public bool PaintingLocked;
        public List<ulong> LockWList;
        public SerializedVector3 LocalPosition;
        public SerializedQuaternion LocalRotation;
        public List<ProtoBuf.PlayerNameID> AuthedPlayers;
        public List<Dictionary<string, object>> ItemList;

        public DeployableComponent(Deployable deployable, SerializedVector3 v3, SerializedQuaternion q)
        {
            Prefab = deployable.GetComponent<BaseNetworkable>().LookupPrefabName();
            LocalPosition = v3;
            LocalRotation = q;
            if (deployable.GetComponent<SleepingBag>())
            {
                SleepingBag sleepingBag = deployable.GetComponent<SleepingBag>();
                DeployedBy = sleepingBag.deployerUserID;
                BagName = sleepingBag.niceName;
                HasOwner = true;
                HasStorage = false;
                HasPainting = false;
                IsCupBoard = false;
            }
            else if (deployable.GetComponent<BuildingPrivlidge>())
            {
                IsCupBoard = true;
                BuildingPrivlidge buildingPrivlidge = deployable.GetComponent<BuildingPrivlidge>();
                AuthedPlayers = new List<ProtoBuf.PlayerNameID>();
                AuthedPlayers = buildingPrivlidge.authorizedPlayers;
            }
            else if (deployable.GetComponent<StorageContainer>())
            {
                HasOwner = false;
                HasStorage = true;
                HasPainting = false;
                IsCupBoard = false;
                StorageContainer storageContainer = deployable.GetComponent<StorageContainer>();
                ItemList = new List<Dictionary<string, object>>();
                foreach (Item item in storageContainer.inventory.itemList)
                {
                    Dictionary<string, object> itemData = new Dictionary<string, object>();
                    itemData.Add("blueprint", item.IsBlueprint());
                    itemData.Add("id", item.info.itemid);
                    itemData.Add("amount", item.amount);
                    ItemList.Add(itemData);
                }
                if (storageContainer.HasSlot(BaseEntity.Slot.Lock))
                {
                    BaseLock baseLock = storageContainer.GetSlot(BaseEntity.Slot.Lock) as BaseLock;
                    if (baseLock == null)
                    {
                        HasCodeLock = false;
                        HasKeyLock = false;
                    }
                    else if (baseLock.GetComponent<CodeLock>())
                    {
                        HasCodeLock = true;
                        HasKeyLock = false;
                        CodeLock codeLock = baseLock.GetComponent<CodeLock>();
                        if (!string.IsNullOrEmpty((string)codeLock.GetFieldValue("code")))
                        {
                            LockCode = (string)codeLock.GetFieldValue("code");
                            LockWList = new List<ulong>();
                            LockWList = (List<ulong>)codeLock.GetFieldValue("whitelistPlayers");
                        }
                    }
                    else if (baseLock.GetComponent<KeyLock>())
                    {
                        HasCodeLock = false;
                        HasKeyLock = true;
                        KeyLock keyLock = baseLock.GetComponent<KeyLock>();
                        int keyCode = (int)keyLock.GetFieldValue("keyCode");
                        keyCode = (bool)keyLock.GetFieldValue("firstKeyCreated") ? keyCode |= 0x80 : (int)keyLock.GetFieldValue("keyCode");
                        LockCode = keyCode.ToString();
                    }
                }
            }
            else if (deployable.GetComponent<Signage>())
            {
                HasOwner = false;
                HasStorage = false;
                HasPainting = true;
                IsCupBoard = false;
                Signage signage = deployable.GetComponent<Signage>();
                byte[] tempImg = FileStorage.server.Get(signage.textureID, FileStorage.Type.png, signage.net.ID);
                if (signage.textureID > 0 && tempImg != null) Painting = tempImg;
                PaintingLocked = signage.IsLocked();
            }
            else
            {
                HasOwner = false;
                HasStorage = false;
                HasPainting = false;
                IsCupBoard = false;
            }
        }

        public override string ToString()
        {
            return String.Format("{0} [pos:{1}, rot:{2}]", Prefab, LocalPosition, LocalRotation);
        }
    }

    [Serializable]
    public class SpawnableComponent : CountedInstance
    {
        public string Prefab;
        public SerializedVector3 LocalPosition;
        public SerializedQuaternion LocalRotation;

        public SpawnableComponent(Spawnable spawnable, SerializedVector3 v3, SerializedQuaternion q)
        {
            Prefab = spawnable.GetComponent<BaseNetworkable>().LookupPrefabName();
            LocalPosition = v3;
            LocalRotation = q;
        }

        public override string ToString()
        {
            return String.Format("{0} [pos:{1}, rot:{2}]", Prefab, LocalPosition, LocalRotation);
        }
    }

    [Serializable]
    public class Structure : CountedInstance
    {
        public string Name;
        public Origo origo;
        public Dictionary<string, StructureComponent> StructureComponents;
        public Dictionary<string, DeployableComponent> DeployableComponents;
        public Dictionary<string, SpawnableComponent> SpawnableComponents;

        public Structure(string name)
        {
            Name = name;
            StructureComponents = new Dictionary<string, StructureComponent>();
            DeployableComponents = new Dictionary<string, DeployableComponent>();
            SpawnableComponents = new Dictionary<string, SpawnableComponent>();
        }

        public void AddComponent(BuildingPart bp)
        {
            if (origo == null)
            {
                origo = new Origo(new SerializedVector3(bp.Location), new SerializedQuaternion(bp.buildingBlock.transform.rotation));
            }
            SerializedVector3 v3 = new SerializedVector3(bp.Location - origo.Position.ToVector3());
            SerializedQuaternion q = new SerializedQuaternion(bp.buildingBlock.transform.rotation);
            StructureComponent component = new StructureComponent(bp, v3, q);
            if (component == null)
            {
                Pluton.Core.Logger.LogDebug("[StructureRecorder] BuildingPart component is null!");
                return;
            }
            if (!StructureComponents.ContainsKey(component.ToString()))
            {
                StructureComponents.Add(component.ToString(), component);
            }
            else
            {
                StructureComponents[component.ToString()] = component;
            }
        }

        public void AddComponent(Deployable deployable)
        {
            if (origo == null)
            {
                origo = new Origo(new SerializedVector3(deployable.transform.position), new SerializedQuaternion(deployable.transform.rotation));
            }
            SerializedVector3 v3 = new SerializedVector3(deployable.transform.position - origo.Position.ToVector3());
            SerializedQuaternion q = new SerializedQuaternion(deployable.transform.rotation);
            DeployableComponent component = new DeployableComponent(deployable, v3, q);
            if (component == null)
            {
                Pluton.Core.Logger.LogDebug("[StructureRecorder] Deployable component is null!");
                return;
            }
            if (!DeployableComponents.ContainsKey(component.ToString()))
            {
                DeployableComponents.Add(component.ToString(), component);
            }
            else
            {
                DeployableComponents[component.ToString()] = component;
            }
        }

        public void AddComponent(Spawnable spawnable)
        {
            if (origo == null)
            {
                origo = new Origo(new SerializedVector3(spawnable.transform.position), new SerializedQuaternion(spawnable.transform.rotation));
            }
            SerializedVector3 v3 = new SerializedVector3(spawnable.transform.position - origo.Position.ToVector3());
            SerializedQuaternion q = new SerializedQuaternion(spawnable.transform.rotation);
            SpawnableComponent component = new SpawnableComponent(spawnable, v3, q);
            if (component == null)
            {
                Pluton.Core.Logger.LogDebug("[StructureRecorder] Deployable component is null!");
                return;
            }
            if (!SpawnableComponents.ContainsKey(component.ToString()))
            {
                SpawnableComponents.Add(component.ToString(), component);
            }
            else
            {
                SpawnableComponents[component.ToString()] = component;
            }
        }

        public void Build(Vector3 spawnAt)
        {
            foreach (StructureComponent component in StructureComponents.Values)
            {
                Vector3 v3 = (component.LocalPosition.ToVector3() + spawnAt);
                BaseEntity ent = GameManager.server.CreateEntity(component.Prefab, v3, component.LocalRotation.ToQuaternion());
                ent.SpawnAsMapEntity();
                BuildingBlock bb = ent.GetComponent<BuildingBlock>();
                bb.blockDefinition = PrefabAttribute.server.Find<Construction>(bb.prefabID);
                bb.grade = component.Grade;
                bb.health = component.Health;
                if (bb.HasSlot(BaseEntity.Slot.Lock))
                {
                    if (component.HasCodeLock)
                    {
                        BaseEntity baseEntity = GameManager.server.CreateEntity("build/locks/lock.code", Vector3.zero, new Quaternion());
                        baseEntity.OnDeployed(bb);
                        if (!string.IsNullOrEmpty(component.LockCode))
                        {
                            CodeLock codeLock = baseEntity.GetComponent<CodeLock>();
                            codeLock.SetFlag(BaseEntity.Flags.Locked, true);
                            codeLock.SetFieldValue("code", component.LockCode);
                            codeLock.SetFieldValue("whitelistPlayers", component.LockWList);
                        }
                        baseEntity.gameObject.Identity();
                        baseEntity.SetParent(bb, "lock");
                        baseEntity.Spawn(true);
                        bb.SetSlot(BaseEntity.Slot.Lock, baseEntity);
                    }
                    else if (component.HasKeyLock)
                    {
                        BaseEntity baseEntity = GameManager.server.CreateEntity("build/locks/lock.key", Vector3.zero, new Quaternion());
                        baseEntity.OnDeployed(bb);
                        int code = int.Parse(component.LockCode);
                        if ((code & 0x80) != 0)
                        {
                            KeyLock keyLock = baseEntity.GetComponent<KeyLock>();
                            keyLock.SetFieldValue("keycode", (code & 0x7F));
                            keyLock.SetFieldValue("firstKeyCreated", true);
                            keyLock.SetFlag(BaseEntity.Flags.Locked, true);
                        }
                        baseEntity.gameObject.Identity();
                        baseEntity.SetParent(bb, "lock");
                        baseEntity.Spawn(true);
                        bb.SetSlot(BaseEntity.Slot.Lock, baseEntity);
                    }
                }
                bb.SendNetworkUpdateImmediate();
            }
            foreach (DeployableComponent component in DeployableComponents.Values)
            {
                Vector3 v3 = (component.LocalPosition.ToVector3() + spawnAt);
                BaseEntity ent = GameManager.server.CreateEntity(component.Prefab, v3, component.LocalRotation.ToQuaternion());
                ent.SpawnAsMapEntity();
                if (component.HasOwner)
                {
                    SleepingBag sleepingBag = ent.GetComponent<SleepingBag>();
                    sleepingBag.deployerUserID = component.DeployedBy;
                    sleepingBag.niceName = component.BagName;
                }
                else if (component.IsCupBoard)
                {
                    BuildingPrivlidge buildingPrivlidge = ent.GetComponent<BuildingPrivlidge>();
                    buildingPrivlidge.authorizedPlayers = component.AuthedPlayers;
                }
                else if (component.HasStorage)
                {
                    StorageContainer storageContainer = ent.GetComponent<StorageContainer>();
                    var items = component.ItemList;
                    foreach (var item in items)
                    {
                        Item newItem = ItemManager.CreateByItemID((int)item["id"], (int)item["amount"], (bool)item["blueprint"]);
                        newItem.MoveToContainer(storageContainer.inventory);
                    }
                    if (ent.HasSlot(BaseEntity.Slot.Lock))
                    {
                        if (component.HasCodeLock)
                        {
                            BaseEntity baseEntity = GameManager.server.CreateEntity("build/locks/lock.code", Vector3.zero, new Quaternion());
                            baseEntity.OnDeployed(ent);
                            if (!string.IsNullOrEmpty(component.LockCode))
                            {
                                CodeLock codeLock = baseEntity.GetComponent<CodeLock>();
                                codeLock.SetFlag(BaseEntity.Flags.Locked, true);
                                codeLock.SetFieldValue("code", component.LockCode);
                                codeLock.SetFieldValue("whitelistPlayers", component.LockWList);
                            }
                            baseEntity.gameObject.Identity();
                            baseEntity.SetParent(ent, "lock");
                            baseEntity.Spawn(true);
                            ent.SetSlot(BaseEntity.Slot.Lock, baseEntity);
                        }
                        else if (component.HasKeyLock)
                        {
                            BaseEntity baseEntity = GameManager.server.CreateEntity("build/locks/lock.key", Vector3.zero, new Quaternion());
                            baseEntity.OnDeployed(ent);
                            int code = int.Parse(component.LockCode);
                            if ((code & 0x80) != 0)
                            {
                                KeyLock keyLock = baseEntity.GetComponent<KeyLock>();
                                keyLock.SetFieldValue("keycode", (code & 0x7F));
                                keyLock.SetFieldValue("firstKeyCreated", true);
                                keyLock.SetFlag(BaseEntity.Flags.Locked, true);
                            }
                            baseEntity.gameObject.Identity();
                            baseEntity.SetParent(ent, "lock");
                            baseEntity.Spawn(true);
                            ent.SetSlot(BaseEntity.Slot.Lock, baseEntity);
                        }
                    }
                }
                else if (component.HasPainting)
                {
                    Signage signage = ent.GetComponent<Signage>();
                    if (component.Painting != null)
                    {
                        byte[] painting = component.Painting;
                        signage.textureID = FileStorage.server.Store(painting, FileStorage.Type.png, signage.net.ID);
                    }
                    if (component.PaintingLocked)
                    {
                        signage.SetFlag(BaseEntity.Flags.Locked, true);
                    }
                    signage.SendNetworkUpdate();
                }
                ent.SendNetworkUpdateImmediate();
            }
            foreach (SpawnableComponent component in SpawnableComponents.Values)
            {
                Vector3 v3 = (component.LocalPosition.ToVector3() + spawnAt);
                BaseEntity ent = GameManager.server.CreateEntity(component.Prefab, v3, component.LocalRotation.ToQuaternion());
                ent.SpawnAsMapEntity();
                ent.SendNetworkUpdateImmediate();
            }
        }

        public void Export()
        {
            using (FileStream stream = new FileStream(Name + ".sps", FileMode.Create))
            {
                BinaryFormatter formatter = new BinaryFormatter();
                formatter.Serialize(stream, this);
            }
        }

        public void RemoveComponent(BuildingPart bp)
        {
            SerializedVector3 v3 = new SerializedVector3(bp.Location - origo.Position.ToVector3());
            SerializedQuaternion q = new SerializedQuaternion(bp.buildingBlock.transform.rotation);
            StructureComponent component = new StructureComponent(bp, v3, q);
            if (StructureComponents.ContainsKey(component.ToString()))
            {
                StructureComponents.Remove(component.ToString());
            }
        }

        public void RemoveComponent(Deployable deployable)
        {
            SerializedVector3 v3 = new SerializedVector3(deployable.transform.position - origo.Position.ToVector3());
            SerializedQuaternion q = new SerializedQuaternion(deployable.transform.rotation);
            DeployableComponent component = new DeployableComponent(deployable, v3, q);
            if (DeployableComponents.ContainsKey(component.ToString()))
            {
                DeployableComponents.Remove(component.ToString());
            }
        }

        public void RemoveComponent(Spawnable spawnable)
        {
            SerializedVector3 v3 = new SerializedVector3(spawnable.transform.position - origo.Position.ToVector3());
            SerializedQuaternion q = new SerializedQuaternion(spawnable.transform.rotation);
            SpawnableComponent component = new SpawnableComponent(spawnable, v3, q);
            if (SpawnableComponents.ContainsKey(component.ToString()))
            {
                SpawnableComponents.Remove(component.ToString());
            }
        }

        public override string ToString()
        {
            return String.Format("Structure ({0}, {1}) - Deployable ({0}, {2}) - Spawnable ({0}, {3})", Name, StructureComponents.Count, DeployableComponents.Count, SpawnableComponents.Count);
        }
    }
}