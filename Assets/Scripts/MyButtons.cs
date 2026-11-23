using UnityEngine;

// Three icon buttons next to the menu: quit, change the background colour, lock the camera rotation.
// MyLSystem adds this script automatically. The icons are in Assets/Resources/Icons.
public class MyButtons : MonoBehaviour
{
    public Color[] backgrounds =
    {
        new Color(0.95f, 0.96f, 0.94f),   // light grey
        new Color(0.12f, 0.13f, 0.15f),   // dark
        new Color(0.62f, 0.78f, 0.92f),   // sky blue
    };

    int backgroundIndex = 0;
    Texture2D quitIcon, backgroundIcon, lockClosedIcon, lockOpenIcon;
    MyCamera myCamera;

    void Start()
    {
        // Resources.Load finds files inside any folder called "Resources" (no file extension).
        quitIcon = Resources.Load<Texture2D>("Icons/quit");
        backgroundIcon = Resources.Load<Texture2D>("Icons/background");
        lockClosedIcon = Resources.Load<Texture2D>("Icons/lock_closed");
        lockOpenIcon = Resources.Load<Texture2D>("Icons/lock_open");
        myCamera = Camera.main.GetComponent<MyCamera>();
    }

    void OnGUI()
    {
        // a column of 40 x 40 buttons, just to the right of the menu (the menu is 360 wide, starting at x = 10)
        float x = 378;
        float size = 40;

        // 1. quit
        if (GUI.Button(new Rect(x, 10, size, size), new GUIContent(quitIcon, "Quit")))
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;   // in the editor: stop Play mode
#else
            Application.Quit();                                // in a built game: close the window
#endif
        }

        // 2. background colour: go to the next colour in the list
        if (GUI.Button(new Rect(x, 10 + 50, size, size), new GUIContent(backgroundIcon, "Background colour")))
        {
            backgroundIndex = (backgroundIndex + 1) % backgrounds.Length;
            Camera.main.backgroundColor = backgrounds[backgroundIndex];
        }

        // 3. camera rotation lock: the icon shows the current state
        Texture2D lockIcon = myCamera.rotationLocked ? lockClosedIcon : lockOpenIcon;
        string lockText = myCamera.rotationLocked ? "Rotation locked" : "Rotation unlocked";
        if (GUI.Button(new Rect(x, 10 + 100, size, size), new GUIContent(lockIcon, lockText)))
        {
            myCamera.rotationLocked = !myCamera.rotationLocked;
        }

        // the name of the button under the mouse, in a dark box so it can be read on any background
        if (GUI.tooltip != "")
        {
            GUI.Box(new Rect(x + size + 6, 10, 140, 25), GUI.tooltip);
        }
    }
}
