using System;
using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;

public class SceneController : MonoBehaviour
{
    Scene front, left, right;
    Scene agriculture, apartment, canal, city, forest, lake, park, suburb;
    private void Awake()
    {
        StartCoroutine(LoadAllScenes());
    }
    IEnumerator LoadAllScenes()
    {
        yield return SceneManager.LoadSceneAsync("Agriculture", LoadSceneMode.Additive);
        agriculture = SceneManager.GetSceneByName("Agriculture");

        yield return SceneManager.LoadSceneAsync("Apartment", LoadSceneMode.Additive);
        apartment = SceneManager.GetSceneByName("Apartment");

        yield return SceneManager.LoadSceneAsync("Canal", LoadSceneMode.Additive);
        canal = SceneManager.GetSceneByName("Canal");

        yield return SceneManager.LoadSceneAsync("City", LoadSceneMode.Additive);
        city = SceneManager.GetSceneByName("City");

        yield return SceneManager.LoadSceneAsync("Forest", LoadSceneMode.Additive);
        forest = SceneManager.GetSceneByName("Forest");

        yield return SceneManager.LoadSceneAsync("Lake", LoadSceneMode.Additive);
        lake = SceneManager.GetSceneByName("Lake");

        yield return SceneManager.LoadSceneAsync("Park", LoadSceneMode.Additive);
        park = SceneManager.GetSceneByName("Park");

        yield return SceneManager.LoadSceneAsync("Suburb", LoadSceneMode.Additive);
        suburb = SceneManager.GetSceneByName("Suburb");

        AllSceneFalse();
    }

    public void AllSceneFalse()
    {
        SetSceneActive(agriculture, false);
        SetSceneActive(apartment, false);
        SetSceneActive(canal, false);
        SetSceneActive(city, false);
        SetSceneActive(forest, false);
        SetSceneActive(lake, false);
        SetSceneActive(park, false);
        SetSceneActive(suburb, false);
    }

    void SetSceneActive(Scene name, bool active)
    {
        foreach(GameObject obj in name.GetRootGameObjects())
        {
            obj.SetActive(active);

            // control with audio listner
            AudioListener al = obj.GetComponent<AudioListener>();
            // LATER NEED TO CHANGE TO ACTIVE
            if(al != null) al.enabled = false;
        }
    }

    public event Action<Scene, Scene, Scene> OnSceneUpdated;
    public void UpdateScenes(Neighbor neighbors)
    {
        // change to set.false
        AllSceneFalse();

        Debug.Log("front: "+neighbors.front + " left: " +neighbors.left+ " right: " + neighbors.right);
        Debug.Log("front: " + GetSceneByTile(neighbors.front) 
            + " left: " + GetSceneByTile(neighbors.left) + " right: " + GetSceneByTile(neighbors.right));


        front = SceneManager.GetSceneByName(GetSceneByTile(neighbors.front));
        left = SceneManager.GetSceneByName(GetSceneByTile(neighbors.left));
        right = SceneManager.GetSceneByName(GetSceneByTile(neighbors.right));

        SetSceneActive(front, true);
        SetSceneActive(left, true);
        SetSceneActive(right, true);

        OnSceneUpdated?.Invoke(front, left, right);
    }

    string GetSceneByTile(string tile)
    {
        switch (tile)
        {
            case "trees": return "forest";
            case "water": return "lake";
            case "built_low": return "suburb";
            case "built_high": return "city";
            case "farmland": return "agriculture";
            case "low_veg": return "park";
            case "shrubs": return "park";
            case "bare_soil": return "suburb";
            default: return "forest";
        }
    }



}
