using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

public class ServerNetworking : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        StartCoroutine(RequestPost());
    }

    IEnumerator RequestPost()
    {
        string url = "http://192.168.1.3:5000/output/uhi";

        byte[] bodyRaw = Encoding.UTF8.GetBytes("{\"tile_id\":0, \"tile_id\":1}");
        using (UnityWebRequest www = new UnityWebRequest(url, "POST"))
        {
            www.uploadHandler = new UploadHandlerRaw(bodyRaw);
            www.downloadHandler = new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");

            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError(www.error);
            }
            else
            {
                Debug.Log(www.downloadHandler.text);
            }
        }
    }
}
