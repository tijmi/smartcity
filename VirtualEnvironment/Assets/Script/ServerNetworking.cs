using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class PlayerData
{
    public float uhi;
    public float wind;
    public string land_use;
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

    [SerializeField]
    private string url = "http://192.168.1.1:5000/input";
        void Start()
    {
        StartCoroutine(RequestLoop());
    }

    IEnumerator RequestLoop()
    {
        while (true)
        {
            yield return StartCoroutine(RequestGet());
            yield return new WaitForSeconds(0.5f);
        }
    }

    IEnumerator RequestPost()
    {
        byte[] bodyRaw = Encoding.UTF8.GetBytes("{}");

        using (UnityWebRequest www = new UnityWebRequest(url, "POST"))
        {
            Debug.Log(www);
            www.uploadHandler = new UploadHandlerRaw(bodyRaw);
            Debug.Log(www.uploadHandler);
            www.downloadHandler = new DownloadHandlerBuffer();
            Debug.Log(www.downloadHandler);
            www.SetRequestHeader("Content-Type", "application/json");
            www.timeout = 3;

            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError(www.error);
            }
            else
            {
                Debug.Log(www.downloadHandler.text);
                result = www.downloadHandler.text;

                //PlayerData newData = JsonUtility.FromJson<PlayerData>(result);
                //lastData = newData;
            }
        }
    }

    IEnumerator RequestGet()
    {
        using (UnityWebRequest www = UnityWebRequest.Get(url))
        {
            www.timeout = 3;
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError(www.error);
            }
            else
            {
                Debug.Log(www.downloadHandler.text);
                result = www.downloadHandler.text;
            }
            }
    }

    //void SplitData(string result)
    //{
    //    PlayerData playerData = JsonUtility.FromJson<PlayerData>(result);

    //    if (playerData == null) {
    //        Debug.LogError("There is no playerData");
    //    }
    //}
}
