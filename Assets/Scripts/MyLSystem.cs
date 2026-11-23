using System.Collections.Generic;
using System.Globalization;
using System.IO;
using UnityEngine;

// Main script. Put it on an empty GameObject in the scene.
// It loads L-systems from the text files in StreamingAssets/LSystems,
// rebuilds the model when a hotkey or the menu changes something, and draws it as lines.
public class MyLSystem : MonoBehaviour
{
    [Header("Current L-system (loaded from a file)")]
    public string title;
    public string axiom;
    public List<Rule> rules = new List<Rule>();
    public int iterations;
    public float angle;
    public float length = 1f;
    public float lengthRatio = 1f;   // each branch is this much shorter than its parent
    public int seed = 1;

    [Header("Settings")]
    public int maxIterations = 12;
    public int maxSymbols = 1000000;
    public Color trunkColour = new Color(0.35f, 0.20f, 0.08f);
    public Color tipColour = new Color(0.15f, 0.50f, 0.10f);

    string[] files;
    int currentFile;
    int symbolCount;
    int segmentCount;
    string message = "";
    bool showMenu = true;
    string axiomText = "";   // what is typed in the menu's text boxes
    string rulesText = "";

    Mesh mesh;
    MyCamera myCamera;

    public int SymbolCount { get { return symbolCount; } }
    public int SegmentCount { get { return segmentCount; } }

    void Start()
    {
        Init();
        LoadFile(0);
    }

    // Creates the mesh, finds the camera and lists the config files.
    public void Init()
    {
        mesh = new Mesh();
        mesh.indexFormat = UnityEngine.Rendering.IndexFormat.UInt32;   // allows more than 65,535 vertices
        gameObject.AddComponent<MeshFilter>().mesh = mesh;
        MeshRenderer meshRenderer = gameObject.AddComponent<MeshRenderer>();
        meshRenderer.material = new Material(Shader.Find("Sprites/Default"));   // unlit, uses vertex colours

        myCamera = Camera.main.GetComponent<MyCamera>();
        if (myCamera == null) myCamera = Camera.main.gameObject.AddComponent<MyCamera>();

        string folder = Path.Combine(Application.streamingAssetsPath, "LSystems");
        files = Directory.GetFiles(folder, "*.txt");
        System.Array.Sort(files);
    }

    // ---------------------------------------------------------------- loading

    // Reads one config file. Each line is  key=value ; lines starting with # are comments.
    public void LoadFile(int index)
    {
        if (index < 0 || index >= files.Length) return;
        currentFile = index;

        // default values, in case the file does not set them
        title = Path.GetFileNameWithoutExtension(files[index]);
        axiom = "F";
        rules.Clear();
        iterations = 4;
        angle = 25f;
        length = 1f;
        lengthRatio = 1f;
        seed = 1;

        foreach (string rawLine in File.ReadAllLines(files[index]))
        {
            string line = rawLine.Trim();
            if (line == "" || line.StartsWith("#")) continue;

            string[] parts = line.Split(new char[] { '=' }, 2);
            if (parts.Length < 2) continue;
            string key = parts[0].Trim();
            string value = parts[1].Trim();

            if (key == "name") title = value;
            else if (key == "axiom") axiom = value;
            else if (key == "iterations") iterations = int.Parse(value);
            else if (key == "angle") angle = ParseFloat(value);
            else if (key == "ratio") lengthRatio = ParseFloat(value);
            else if (key == "rule")
            {
                Rule rule = ParseRule(value);
                if (rule != null) rules.Add(rule);
            }
        }

        FillEditor();
        message = "Loaded " + Path.GetFileName(files[index]);
        Rebuild();
    }

    // "F:F[+F]F[-F]F"  or, with a probability,  "F:0.33:F[+F]F"
    // Returns null if the text is not a rule.
    Rule ParseRule(string value)
    {
        string[] p = value.Split(':');
        if (p[0].Trim().Length != 1) return null;   // the left side must be one symbol
        char symbol = p[0].Trim()[0];

        if (p.Length == 2) return new Rule(symbol, p[1].Trim(), 1f);

        float probability;
        if (p.Length == 3 && float.TryParse(p[1], NumberStyles.Float, CultureInfo.InvariantCulture, out probability))
            return new Rule(symbol, p[2].Trim(), probability);

        return null;
    }

    // Always read "25.7" with a dot, whatever the language settings of the computer.
    float ParseFloat(string s)
    {
        return float.Parse(s, CultureInfo.InvariantCulture);
    }

    // ---------------------------------------------------------------- building

    // String rewriting -> turtle -> mesh -> camera.
    public void Rebuild()
    {
        string symbols = MyRewriter.Generate(axiom, rules, iterations, seed, maxSymbols);

        // Too long? Go back one iteration until it fits.
        while (symbols == null && iterations > 0)
        {
            iterations--;
            message = "Too many symbols - iterations limited to " + iterations;
            symbols = MyRewriter.Generate(axiom, rules, iterations, seed, maxSymbols);
        }
        if (symbols == null) return;

        List<Segment> segments = MyTurtle.Draw(symbols, angle, length, lengthRatio);
        symbolCount = symbols.Length;
        segmentCount = segments.Count;

        BuildMesh(segments);
        myCamera.Frame(mesh.bounds);
    }

    // All lines go into ONE mesh (one draw call), coloured from brown (trunk) to green (tips).
    void BuildMesh(List<Segment> segments)
    {
        int maxDepth = 1;
        foreach (Segment s in segments) maxDepth = Mathf.Max(maxDepth, s.depth);

        List<Vector3> vertices = new List<Vector3>();
        List<Color> colours = new List<Color>();
        List<int> indices = new List<int>();

        foreach (Segment s in segments)
        {
            Color c = Color.Lerp(trunkColour, tipColour, (float)s.depth / maxDepth);
            indices.Add(vertices.Count);
            vertices.Add(s.start);
            colours.Add(c);
            indices.Add(vertices.Count);
            vertices.Add(s.end);
            colours.Add(c);
        }

        mesh.Clear();
        mesh.SetVertices(vertices);
        mesh.SetColors(colours);
        mesh.SetIndices(indices, MeshTopology.Lines, 0);
        mesh.RecalculateBounds();
    }

    // ---------------------------------------------------------------- hotkeys

    // Hotkeys use only the arrow keys and the number keys, so letters are free for typing in the menu.
    void Update()
    {
        // While the cursor is in a text box, the keys belong to the text box.
        if (GUIUtility.keyboardControl != 0) return;

        // 1-9 and 0 (top row or numpad) load the config files
        for (int i = 0; i < 10; i++)
        {
            KeyCode key = (i < 9) ? KeyCode.Alpha1 + i : KeyCode.Alpha0;
            KeyCode pad = (i < 9) ? KeyCode.Keypad1 + i : KeyCode.Keypad0;
            if (Input.GetKeyDown(key) || Input.GetKeyDown(pad)) LoadFile(i);
        }

        bool shift = Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift);
        bool changed = false;

        if (!shift)
        {
            // Up / Down: iterations      Left / Right: angle
            if (Input.GetKeyDown(KeyCode.UpArrow) && iterations < maxIterations) { iterations++; changed = true; }
            if (Input.GetKeyDown(KeyCode.DownArrow) && iterations > 0) { iterations--; changed = true; }
            if (Input.GetKeyDown(KeyCode.RightArrow)) { angle = Mathf.Min(angle + 1f, 180f); changed = true; }
            if (Input.GetKeyDown(KeyCode.LeftArrow)) { angle = Mathf.Max(angle - 1f, 0f); changed = true; }
        }
        else
        {
            // Shift + Up / Down: random seed      Shift + Left / Right: branch length ratio
            if (Input.GetKeyDown(KeyCode.UpArrow)) { seed++; changed = true; }
            if (Input.GetKeyDown(KeyCode.DownArrow) && seed > 1) { seed--; changed = true; }
            if (Input.GetKeyDown(KeyCode.RightArrow)) { lengthRatio = Mathf.Min(lengthRatio + 0.05f, 1.2f); changed = true; }
            if (Input.GetKeyDown(KeyCode.LeftArrow)) { lengthRatio = Mathf.Max(lengthRatio - 0.05f, 0.3f); changed = true; }
        }

        if (changed)
        {
            message = "";
            Rebuild();
        }
    }

    void TakeScreenshot()
    {
        string folder = Path.Combine(Application.dataPath, "..", "Screenshots");
        Directory.CreateDirectory(folder);
        string path = Path.Combine(folder, title.Replace(" ", "_") + "_n" + iterations + ".png");
        ScreenCapture.CaptureScreenshot(path);
        message = "Saved " + path;
    }

    // ---------------------------------------------------------------- rule editor

    // Writes the current axiom and rules into the text boxes, in the same format as the files.
    void FillEditor()
    {
        axiomText = axiom;
        rulesText = "";
        foreach (Rule r in rules)
        {
            if (r.probability < 1f)
                rulesText += r.symbol + ":" + r.probability.ToString(CultureInfo.InvariantCulture) + ":" + r.successor + "\n";
            else
                rulesText += r.symbol + ":" + r.successor + "\n";
        }
    }

    // Reads the text boxes, one rule per line. If a line is wrong, nothing changes.
    void ApplyEditor()
    {
        List<Rule> newRules = new List<Rule>();
        foreach (string rawLine in rulesText.Split('\n'))
        {
            string line = rawLine.Trim();
            if (line == "") continue;

            Rule rule = ParseRule(line);
            if (rule == null)
            {
                message = "Cannot read rule: " + line;
                return;
            }
            newRules.Add(rule);
        }

        axiom = axiomText.Trim();
        rules = newRules;
        message = "Rules applied";
        Rebuild();
    }

    // ---------------------------------------------------------------- menu

    void OnGUI()
    {
        // A click outside the text boxes takes the cursor out of them, so the hotkeys work again.
        // (A click on a text box puts the cursor back, because the text box handles the click after this line.)
        if (Event.current.type == EventType.MouseDown) GUIUtility.keyboardControl = 0;

        if (!showMenu)
        {
            if (GUI.Button(new Rect(10, 10, 110, 30), "Show menu")) showMenu = true;
            return;
        }

        GUILayout.BeginArea(new Rect(10, 10, 360, Screen.height - 20), GUI.skin.box);

        GUILayout.Label((currentFile + 1) + ". " + title);
        GUILayout.BeginHorizontal();
        if (GUILayout.Button("< Previous file")) LoadFile((currentFile + files.Length - 1) % files.Length);
        if (GUILayout.Button("Next file >")) LoadFile((currentFile + 1) % files.Length);
        GUILayout.EndHorizontal();

        // rule editor
        GUILayout.Space(6);
        GUILayout.Label("Axiom");
        axiomText = GUILayout.TextField(axiomText);
        GUILayout.Label("Rules, one per line:   F:F[+F]F   or   F:0.5:F[+F]");
        rulesText = GUILayout.TextArea(rulesText, GUILayout.Height(90));
        GUILayout.BeginHorizontal();
        if (GUILayout.Button("Apply rules")) ApplyEditor();
        if (GUILayout.Button("Reload file")) LoadFile(currentFile);
        GUILayout.EndHorizontal();

        // parameters: if a slider has moved, rebuild
        GUILayout.Space(6);
        int newIterations = Mathf.RoundToInt(Slider("Iterations", iterations, 0, maxIterations, "0"));
        float newAngle = Slider("Angle", angle, 0f, 180f, "0.0");
        float newRatio = Slider("Length ratio", lengthRatio, 0.3f, 1.2f, "0.00");
        if (newIterations != iterations || newAngle != angle || newRatio != lengthRatio)
        {
            iterations = newIterations;
            angle = newAngle;
            lengthRatio = newRatio;
            message = "";
            Rebuild();
        }

        GUILayout.BeginHorizontal();
        GUILayout.Label("Seed: " + seed);
        if (GUILayout.Button("New seed")) { seed = Random.Range(1, 10000); message = ""; Rebuild(); }
        GUILayout.EndHorizontal();

        // view
        GUILayout.BeginHorizontal();
        myCamera.autoRotate = GUILayout.Toggle(myCamera.autoRotate, "Auto rotate");
        if (GUILayout.Button("Screenshot")) TakeScreenshot();
        if (GUILayout.Button("Hide menu")) showMenu = false;
        GUILayout.EndHorizontal();

        // information and help
        GUILayout.Space(6);
        GUILayout.Label(symbolCount + " symbols, " + segmentCount + " lines");
        if (message != "") GUILayout.Label(message);
        GUILayout.Label("Hotkeys\n"
                      + "1-9, 0 (or numpad)      load file\n"
                      + "Up / Down               iterations\n"
                      + "Left / Right            angle\n"
                      + "Shift + Up / Down       random seed\n"
                      + "Shift + Left / Right    length ratio\n"
                      + "Right mouse drag        rotate the view\n"
                      + "Mouse wheel             zoom");

        GUILayout.EndArea();
    }

    // One line of the menu: name, slider, value.
    float Slider(string name, float value, float min, float max, string format)
    {
        GUILayout.BeginHorizontal();
        GUILayout.Label(name, GUILayout.Width(85));
        value = GUILayout.HorizontalSlider(value, min, max, GUILayout.Width(180));
        GUILayout.Label(value.ToString(format));
        GUILayout.EndHorizontal();
        return value;
    }
}
