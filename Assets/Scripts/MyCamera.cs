using UnityEngine;
using UnityEngine.Rendering.Universal;

public class MyCamera : MonoBehaviour
{
    public float yaw = 0f;
    public float pitch = 0f;
    public bool autoRotate = false;
    public bool rotationLocked = false;   

    Vector3 target;
    float distance = 10f;
    Camera cam;

    void Awake()
    {
        cam = GetComponent<Camera>();
        cam.clearFlags = CameraClearFlags.SolidColor;
        cam.backgroundColor = new Color(0.95f, 0.96f, 0.94f);

        
        cam.GetUniversalAdditionalCameraData().renderPostProcessing = false;
    }

    
    public void Frame(Bounds bounds)
    {
        if (cam == null) Awake();
        target = bounds.center;
        float radius = bounds.extents.magnitude;
        
        float halfFov = cam.fieldOfView * 0.5f * Mathf.Deg2Rad;
        if (cam.aspect < 1f) halfFov = Mathf.Atan(Mathf.Tan(halfFov) * cam.aspect);
        distance = radius / Mathf.Sin(halfFov) * 1.05f;
        UpdatePosition();
    }

    void LateUpdate()
    {
        
        if (!rotationLocked)
        {
            if (Input.GetMouseButton(1))
            {
                yaw += Input.GetAxis("Mouse X") * 4f;
                pitch -= Input.GetAxis("Mouse Y") * 4f;
                pitch = Mathf.Clamp(pitch, -80f, 80f);
            }
            if (autoRotate) yaw += 15f * Time.deltaTime;
        }

        float scroll = Input.mouseScrollDelta.y;
        if (scroll != 0f) distance *= (scroll > 0f) ? 0.9f : 1.1f;

        UpdatePosition();
    }

    void UpdatePosition()
    {
        Quaternion rotation = Quaternion.Euler(pitch, yaw, 0f);
        transform.rotation = rotation;
        transform.position = target - rotation * Vector3.forward * distance;
    }
}
