using System.Collections.Generic;
using System.Globalization;
using System.IO;
using UnityEngine;

public class MyLSystem : MonoBehaviour
{
    [Header("Current L-system (loaded from a file)")]
    public string title;
    public string axiom;
    public List<Rule> rules = new List<Rule>();
    public int iterations;
    public float angle;
    public float length = 1f;
    public float lengthRatio = 1f;   
    public int seed = 1;

    [Header("Settings")]
    public int maxIterations = 12;
    public int maxSymbols = 1000000;
    public Color trunkColour = new Color(0.35f, 0.20f, 0.08f);
    public Color tipColour = new Color(0.15f, 0.50f, 0.10f);

    [Header("3D branches and leaves")]
    public bool solidMode = false;     
    public bool showLeaves = true;
    public float trunkWidth = 0.6f;    // radius of the trunk, in % of the plant's size
    public float widthRatio = 0.7f;    // each branch level is this much thinner

    // length of a leaf, in % of the plant's size
    public float leafSize = 2f;        
    public Color barkColour = new Color(0.45f, 0.30f, 0.15f);
    public Color leafColour = new Color(0.30f, 0.65f, 0.20f);
    // each branch is a 6-sided tube
    const int sides = 6;               

    string[] files;
    int currentFile;
    int symbolCount;
    int segmentCount;
    int leafCount;
    string message = "";
    bool showMenu = true;
    string axiomText = ""; 
    string rulesText = "";

    Mesh mesh;
    MeshRenderer meshRenderer;
    Material lineMaterial;
    Material barkMaterial;
    Material leafMaterial;
    MyCamera myCamera;

    public int SymbolCount { get { return symbolCount; } }
    public int SegmentCount { get { return segmentCount; } }

    void Start()
    {
        Init();
        LoadFile(0);
    }

    // Creates the mesh and materials, finds the camera and lists the config files.
    public void Init()
    {
        mesh = new Mesh();
        mesh.indexFormat = UnityEngine.Rendering.IndexFormat.UInt32;   // allows more than 65,535 vertices
        gameObject.AddComponent<MeshFilter>().mesh = mesh;
        meshRenderer = gameObject.AddComponent<MeshRenderer>();

        lineMaterial = new Material(Shader.Find("Sprites/Default"));   // unlit, uses vertex colours
        barkMaterial = MakeLitMaterial(barkColour);
        leafMaterial = MakeLitMaterial(leafColour);

        myCamera = Camera.main.GetComponent<MyCamera>();
        if (myCamera == null) myCamera = Camera.main.gameObject.AddComponent<MyCamera>();
        if (GetComponent<MyButtons>() == null) gameObject.AddComponent<MyButtons>();   // quit / background / lock buttons

        string folder = Path.Combine(Application.streamingAssetsPath, "LSystems");
        files = Directory.GetFiles(folder, "*.txt");
        System.Array.Sort(files);
    }

    // A material lit by the scene's light, with one colour, drawn from both sides.
    Material MakeLitMaterial(Color colour)
    {
        // Copy the material in Assets/Resources/Materials (URP Simple Lit).
        // It must be a real material asset: Unity leaves out of a build every shader that no asset uses,
        // so Shader.Find("Universal Render Pipeline/Simple Lit") would return null in the built game.
        Material m = new Material(Resources.Load<Material>("Materials/PlantLit"));
        m.SetColor("_BaseColor", colour);
        m.SetFloat("_Cull", 0f);   // 0 = do not hide back faces, so a leaf is seen from both sides
        return m;
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

        List<Leaf> leaves;
        List<Segment> segments = MyTurtle.Draw(symbols, angle, length, lengthRatio, out leaves);
        symbolCount = symbols.Length;
        segmentCount = segments.Count;
        leafCount = (solidMode && showLeaves) ? leaves.Count : 0;

        if (solidMode) BuildSolidMesh(segments, leaves);
        else BuildMesh(segments);
        myCamera.Frame(mesh.bounds);
    }

    // Lines: all lines go into ONE mesh (one draw call), coloured from brown (trunk) to green (tips).
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
        mesh.subMeshCount = 1;
        mesh.SetVertices(vertices);
        mesh.SetColors(colours);
        mesh.SetIndices(indices, MeshTopology.Lines, 0);
        mesh.RecalculateBounds();
        meshRenderer.materials = new Material[] { lineMaterial };
    }

    // ---------------------------------------------------------------- 3D branches and leaves

    // Every segment becomes a thin tube and every leaf a small diamond.
    // The mesh has two parts (sub-meshes): 0 = branches (bark material), 1 = leaves (leaf material).
    void BuildSolidMesh(List<Segment> segments, List<Leaf> leaves)
    {
        // How big is the plant? The trunk and the leaves are sized as a % of this,
        // so they look the same on a small plant and on a big one.
        Bounds box = new Bounds(Vector3.zero, Vector3.zero);
        foreach (Segment s in segments)
        {
            box.Encapsulate(s.start);
            box.Encapsulate(s.end);
        }
        float plantSize = Mathf.Max(box.size.magnitude, 1f);
        float trunkRadius = plantSize * trunkWidth / 100f;
        float leafLength = plantSize * leafSize / 100f;

        List<Vector3> vertices = new List<Vector3>();
        List<Vector3> normals = new List<Vector3>();
        List<int> branchTriangles = new List<int>();
        List<int> leafTriangles = new List<int>();

        foreach (Segment s in segments)
        {
            // deeper branches are thinner: radius = trunk radius * 0.7^depth
            float radius = trunkRadius * Mathf.Pow(widthRatio, s.depth);
            AddBranch(s, radius, vertices, normals, branchTriangles);
        }
        if (showLeaves)
        {
            foreach (Leaf leaf in leaves) AddLeaf(leaf, leafLength, vertices, normals, leafTriangles);
        }

        mesh.Clear();
        mesh.subMeshCount = 2;
        mesh.SetVertices(vertices);
        mesh.SetNormals(normals);
        mesh.SetTriangles(branchTriangles, 0);
        mesh.SetTriangles(leafTriangles, 1);
        mesh.RecalculateBounds();
        meshRenderer.materials = new Material[] { barkMaterial, leafMaterial };
    }

    // A tube around one segment: a ring of points at the start, a ring at the end, joined by rectangles.
    void AddBranch(Segment s, float radius, List<Vector3> vertices, List<Vector3> normals, List<int> triangles)
    {
        Vector3 direction = (s.end - s.start).normalized;

        // Two directions at right angles to the branch (and to each other), from the cross product.
        Vector3 side1 = Vector3.Cross(direction, Vector3.forward);
        if (side1.magnitude < 0.01f) side1 = Vector3.Cross(direction, Vector3.right);   // branch points along Z
        side1.Normalize();
        Vector3 side2 = Vector3.Cross(direction, side1);

        int first = vertices.Count;
        for (int i = 0; i < sides; i++)
        {
            // a point on a circle: cos and sin of the angle around the branch
            float a = i * 2f * Mathf.PI / sides;
            Vector3 outwards = side1 * Mathf.Cos(a) + side2 * Mathf.Sin(a);
            vertices.Add(s.start + outwards * radius);   // vertex first + 2i      (bottom ring)
            vertices.Add(s.end + outwards * radius);     // vertex first + 2i + 1  (top ring)
            normals.Add(outwards);
            normals.Add(outwards);
        }

        for (int i = 0; i < sides; i++)
        {
            int next = (i + 1) % sides;      // the last side joins back to the first
            int bottom = first + 2 * i;
            int top = bottom + 1;
            int nextBottom = first + 2 * next;
            int nextTop = nextBottom + 1;
            // one rectangle = two triangles
            triangles.Add(bottom); triangles.Add(nextTop); triangles.Add(top);
            triangles.Add(bottom); triangles.Add(nextBottom); triangles.Add(nextTop);
        }
    }

    // A diamond-shaped leaf pointing the same way as the turtle.
    void AddLeaf(Leaf leaf, float size, List<Vector3> vertices, List<Vector3> normals, List<int> triangles)
    {
        Quaternion r = leaf.rotation;
        Vector3 p = leaf.position;
        int first = vertices.Count;

        // The corners are written in the turtle's own frame (Y = forward), then turned with r.
        vertices.Add(p);                                                    // base
        vertices.Add(p + r * new Vector3(-0.3f * size, 0.5f * size, 0f));   // left
        vertices.Add(p + r * new Vector3(0f, size, 0f));                    // tip
        vertices.Add(p + r * new Vector3(0.3f * size, 0.5f * size, 0f));    // right
        Vector3 normal = r * Vector3.back;
        for (int i = 0; i < 4; i++) normals.Add(normal);

        triangles.Add(first); triangles.Add(first + 1); triangles.Add(first + 2);
        triangles.Add(first); triangles.Add(first + 2); triangles.Add(first + 3);
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

        // 3D branches and leaves
        GUILayout.Space(6);
        bool newSolid = GUILayout.Toggle(solidMode, "3D branches and leaves");
        bool newLeaves = showLeaves;
        float newWidth = trunkWidth;
        float newLeafSize = leafSize;
        if (solidMode)
        {
            newLeaves = GUILayout.Toggle(showLeaves, "Leaves");
            newWidth = Slider("Trunk width", trunkWidth, 0.2f, 3f, "0.0");
            newLeafSize = Slider("Leaf size", leafSize, 0.5f, 5f, "0.0");
        }
        if (newSolid != solidMode || newLeaves != showLeaves || newWidth != trunkWidth || newLeafSize != leafSize)
        {
            solidMode = newSolid;
            showLeaves = newLeaves;
            trunkWidth = newWidth;
            leafSize = newLeafSize;
            Rebuild();
        }

        // view
        GUILayout.Space(6);
        GUILayout.BeginHorizontal();
        myCamera.autoRotate = GUILayout.Toggle(myCamera.autoRotate, "Auto rotate");
        if (GUILayout.Button("Screenshot")) TakeScreenshot();
        if (GUILayout.Button("Hide menu")) showMenu = false;
        GUILayout.EndHorizontal();

        // information and help
        GUILayout.Space(6);
        string counts = symbolCount + " symbols, " + segmentCount + " branches";
        if (leafCount > 0) counts += ", " + leafCount + " leaves";
        GUILayout.Label(counts);
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
