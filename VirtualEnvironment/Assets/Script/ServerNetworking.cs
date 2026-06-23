using System;
using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using TMPro;

[Serializable]
public class PlayerData
{
    public float uhi;
    public float wind;
    public string land_use;
    public float death;
    public Neighbor neighbors;
}
[Serializable]
public class Neighbor
{
    public string front;
    public string left;
    public string right;
}

public class ServerNetworking : MonoBehaviour
{
    private string result = "";
    private PlayerData lastData = null;
    UdpClient udp;
    Thread thread;
    string latestJson = null;
    readonly object lockObj = new object();

    [SerializeField]
    private string url = "http://192.168.1.1:5000/input";

    [SerializeField] public List<HeatLightController> heatLightControllers = new List<HeatLightController>();
    [SerializeField] public SceneController sceneController;
    [SerializeField] public TMP_Text UHI;

    [Tooltip("If true, smoothly transitions to the target value instead of snapping instantly")]
    public bool smoothTransition = true;
    public float transitionSpeed = 3f;

    public static ServerNetworking Instance;
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        } else Destroy(gameObject);
    }


    void Start()
    {
        sceneController.OnSceneUpdated += UpdateHeatLightControllers;

        udp = new UdpClient(5005);
        thread = new Thread(() => {
            IPEndPoint ep = new IPEndPoint(IPAddress.Any, 0);
            while (true)
            {
                byte[] data = udp.Receive(ref ep);
                print($"Received {data.Length} bytes from {ep.Address}:{ep.Port}");
                print($"Data: {Encoding.UTF8.GetString(data)}");
                string json = Encoding.UTF8.GetString(data);
                lock (lockObj) { latestJson = json; }
            }
        });
        thread.IsBackground = true;
        thread.Start();
    }

    void Update()
    {
        // Test code
        if (Input.GetKeyDown(KeyCode.T))
        {
            string testJson = "{\"uhi\":2.5,\"wind\":3.0,\"land_use\":\"trees\",\"death\":10,\"neighbors\":{\"front\":\"trees\",\"left\":\"water\",\"right\":\"built_low\"}}";
            PlayerData testData = JsonUtility.FromJson<PlayerData>(testJson);
            ShareData(testData);
        }

        if (Input.GetKeyDown(KeyCode.R))
        {
            string testJson = "{\"uhi\":0,\"wind\":3.0,\"land_use\":\"bare_soil\",\"death\":10,\"neighbors\":{\"front\":\"bare_soil\",\"left\":\"farmland\",\"right\":\"low_veg\"}}";
            PlayerData testData = JsonUtility.FromJson<PlayerData>(testJson);
            ShareData(testData);
        }
        if (Input.GetKeyDown(KeyCode.E))
        {
            string testJson = "{\"uhi\":0,\"wind\":3.0,\"land_use\":\"bare_soil\",\"death\":10,\"neighbors\":{\"front\":\"bare_soil\",\"left\":\"bare_soil\",\"right\":\"low_veg\"}}";
            PlayerData testData = JsonUtility.FromJson<PlayerData>(testJson);
            ShareData(testData);
        }

        string json;
        lock (lockObj)
        {
            json = latestJson;
            latestJson = null;
        }
        if (json != null)
        {
            PlayerData playerData = JsonUtility.FromJson<PlayerData>(json);
            if(lastData != null &&
                lastData.uhi == playerData.uhi&&
                lastData.land_use == playerData.land_use&&
                lastData.neighbors?.front == playerData.neighbors?.front)
            {
                return;
            }
            else
            {
                lastData = playerData;
                ShareData(playerData);
            }
                
        }
    }


    void ShareData(PlayerData data)
    {
        if (data == null)
        {
            Debug.LogError("There is no playerData");
            return;
        }


        // send uhi to HeatLightController
        foreach (HeatLightController hlc in heatLightControllers)
        {
            if (smoothTransition)
            {
                // Smoothly move heatLevel toward the target each frame
                float newHeat = Mathf.MoveTowards(hlc.heatLevel, data.uhi, transitionSpeed * Time.deltaTime);
                hlc.SetHeatLevel(newHeat);
            }
            else
            {
                // Snap instantly
                hlc.SetHeatLevel(data.uhi);
            }
        }

        // send neighbors
        sceneController.UpdateScenes(data.neighbors);

        // display uhi value
        UpdateUI(data.uhi);
        Debug.Log("UHI: " + data.uhi);
    }

    public void UpdateHeatLightControllers(Scene front, Scene left, Scene right)
    {
        heatLightControllers.Clear();
        AddHeatLightFromScene(front);
        AddHeatLightFromScene(left);
        AddHeatLightFromScene(right);

    }

    public void AddHeatLightFromScene(Scene scene)
    {
        foreach (GameObject obj in scene.GetRootGameObjects())
        {
            HeatLightController hlc = obj.GetComponentInChildren<HeatLightController>();
            if (hlc != null && !heatLightControllers.Contains(hlc))
            {
                heatLightControllers.Add(hlc);
            }
        }
    }

    private void UpdateUI(float uhi) { 
        UHI.text = "UHI: " + uhi;
    }

}
