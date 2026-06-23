using UnityEngine;
using UnityEngine.SceneManagement;

public class CameraController : MonoBehaviour
{
    Camera frontC, leftC, rightC;

    [SerializeField] public SceneController sceneController;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        sceneController.OnSceneUpdated += UpdateCameras;

    }

    void UpdateCameras(Scene front, Scene left, Scene right)
    {
        // clean all cameras
        AllCamerasFalse();

        // find camera
        frontC = FindCamera(front, "Front");
        leftC = FindCamera(left, "Left");
        rightC = FindCamera(right, "Right");

        if (frontC != null)
        {
            frontC.enabled = true;
            frontC.targetDisplay = 0;
        }
        if (leftC != null)
        {
            leftC.enabled = true;
            leftC.targetDisplay = 1;
        }
        if (rightC != null)
        {
            rightC.enabled = true;
            rightC.targetDisplay = 2;
        }

    }
    void AllCamerasFalse()
    {
        if (frontC != null) frontC.enabled = false;
        if (leftC != null) leftC.enabled = false;
        if (rightC != null) rightC.enabled = false;
    }

    Camera FindCamera(Scene scene, string cameraName)
    {
        foreach (GameObject obj in scene.GetRootGameObjects())
        {
            if (obj.name.ToLower() == cameraName.ToLower())
            {
                Debug.Log("Scene: " + scene.name + "Camera name: " + cameraName);
                return obj.GetComponent<Camera>();
                
            }
        }
        return null;
    }

    private void Update()
    {
        if (Input.GetKeyUp(KeyCode.Alpha7)) { Display.displays[0].Activate(); }
        if (Input.GetKeyUp(KeyCode.Alpha8)) { Display.displays[1].Activate(); }
        if (Input.GetKeyUp(KeyCode.Alpha9)) { Display.displays[2].Activate(); }
    }


}
