using UnityEngine;

[RequireComponent(typeof(Light))]
public class HeatLightController : MonoBehaviour
{
    [Header("Heat Range")]
    [Tooltip("0 = normal temperature, 5 = max heat")]
    [Range(0f, 5f)]
    public float heatLevel = 0f;

    [Header("Colors")]
    public Color normalColor = new Color(1f, 0.96f, 0.88f); // soft white/warm white
    public Color maxHeatColor = new Color(1f, 0.25f, 0.05f); // red-orange

    [Header("Optional: Intensity Scaling")]
    public bool scaleIntensity = false;
    public float normalIntensity = 1f;
    public float maxHeatIntensity = 3f;

    private Light _light;

    void Awake()
    {
        _light = GetComponent<Light>();
    }

    void Update()
    {
        ApplyHeat(heatLevel);
    }

    public void ApplyHeat(float value)
    {
        value = Mathf.Clamp(value, 0f, 5f);
        float t = value / 5f; // normalize to 0-1

        _light.color = Color.Lerp(normalColor, maxHeatColor, t);

        if (scaleIntensity)
        {
            _light.intensity = Mathf.Lerp(normalIntensity, maxHeatIntensity, t);
        }
    }

    // Call this from UI sliders, gameplay events, etc.
    public void SetHeatLevel(float value)
    {
        heatLevel = Mathf.Clamp(value, 0f, 5f);
        ApplyHeat(heatLevel);
    }
}