using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class Network : MonoBehaviour
{
    private void Start()
    {
        StartCoroutine(unityWebReqeustPost());
    }
    IEnumerator unityWebReqeustPost()
    {
        string hardware_url = "http://192.168.1.1:5000/input";
        string software_url = "http://192.168.1.3:5000/output/uhi";
        WWWForm form = new WWWForm();
        form.AddField("myField", "myData");

        UnityWebRequest www = UnityWebRequest.Post(software_url, form);

        // wait response
        yield return www.SendWebRequest();



        if(www.result == UnityWebRequest.Result.Success)
        {
            Debug.Log(www.downloadHandler.text);
        }
        else
        {
            Debug.Log("ERROR: " + www.error);
        }
    }
}
