using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine.SceneManagement;

public class CityReceiver : MonoBehaviour {
    UdpClient udp;
    Thread thread;
    string latestJson = null;
    readonly object lockObj = new object();
    string[] scenes = { "Agriculture", "Apartment", "Canal", "City", "Forest", "Lake", "Park", "Suburb", "Test" };

    void Start() {
        udp = new UdpClient(5005);
        thread = new Thread(() => {
            IPEndPoint ep = new IPEndPoint(IPAddress.Any, 0);
            while (true) {
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

    void Update() {
        string json;
        lock (lockObj) {
            json = latestJson;
            latestJson = null;
        }
        if (json != null) {
            var state = JsonUtility.FromJson<land_use>(json);
            ApplyLanduse(state);
        }
    }

    void ApplyLanduse(land_use state) {
        SceneManager.LoadScene("Canal");
        if("char" in land_use) {
            // Apply land use changes to the scene based on the received state
            // This is a placeholder for actual implementation
            Debug.Log("Applying land use changes...");
        }
        
        
    }

    void OnApplicationQuit() {
        thread.Abort();
        udp.Close();
    }
}

[System.Serializable]
public class CityState {
    public int tick;
    public int[] grid;
}