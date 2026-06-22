using System;
using System.Collections;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;
using UnityEngine.Networking;

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

    [SerializeField]
    public HeatLightController heatLightController;

    [Tooltip("If true, smoothly transitions to the target value instead of snapping instantly")]
    public bool smoothTransition = true;
    public float transitionSpeed = 3f;

    void Start()
    {
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
        string json;
        lock (lockObj)
        {
            json = latestJson;
            latestJson = null;
        }
        if (json != null)
        {
            PlayerData playerData = JsonUtility.FromJson<PlayerData>(json);
            lastData = playerData;
            ShareData(playerData);
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
        if (smoothTransition)
        {
            // Smoothly move heatLevel toward the target each frame
            float newHeat = Mathf.MoveTowards(heatLightController.heatLevel, data.uhi, transitionSpeed * Time.deltaTime);
            heatLightController.SetHeatLevel(newHeat);
        }
        else
        {
            // Snap instantly
            heatLightController.SetHeatLevel(data.uhi);
        }
    }
}
