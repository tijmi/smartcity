using UnityEngine;

public class UHILightController : MonoBehaviour
{
    [Tooltip("Drag the light's HeatLightController here")]
    public HeatLightController heatLight;

    [Tooltip("If true, smoothly transitions to the target value instead of snapping instantly")]
    public bool smoothTransition = true;
    public float transitionSpeed = 3f;

    private float _targetHeat = 0f;

    void Update()
    {
        // Check number keys 0-5
        if (Input.GetKeyDown(KeyCode.Alpha0)) _targetHeat = 0f;
        if (Input.GetKeyDown(KeyCode.Alpha1)) _targetHeat = 1f;
        if (Input.GetKeyDown(KeyCode.Alpha2)) _targetHeat = 2f;
        if (Input.GetKeyDown(KeyCode.Alpha3)) _targetHeat = 3f;
        if (Input.GetKeyDown(KeyCode.Alpha4)) _targetHeat = 4f;
        if (Input.GetKeyDown(KeyCode.Alpha5)) _targetHeat = 5f;

        if (heatLight == null) return;

        if (smoothTransition)
        {
            // Smoothly move heatLevel toward the target each frame
            float newHeat = Mathf.MoveTowards(heatLight.heatLevel, _targetHeat, transitionSpeed * Time.deltaTime);
            heatLight.SetHeatLevel(newHeat);
        }
        else
        {
            // Snap instantly
            heatLight.SetHeatLevel(_targetHeat);
        }
    }
}
