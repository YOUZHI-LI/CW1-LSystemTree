# L-System Plant Generator (CW1, Mathematics and Graphics for Computer Games 1)

Youzhi Li, MSc Computer Game Programming, Goldsmiths, University of London.

A small L-system program in Unity (C#). It reads L-systems from text files, rewrites the axiom with the
production rules and draws the result with a 2D/3D turtle, as lines or as 3D branches with leaves.

- Report: `Report/YouzhiLi-L-system-2026.pdf`
- Video: https://youtu.be/BUrIMRFPZxQ

## Running it

- **Built version (Windows):** unzip `YouzhiLi-LSystemTree-Windows-Build.zip` and run `LSystemTree.exe`.
- **Unity project:** open this folder with Unity 6000.3.25f1 (Unity 6.3 LTS, URP), open
  `Assets/Scenes/SampleScene` and press Play. The `LSystem` object in the scene holds the `MyLSystem` script.

## Controls

| Key | Action |
|---|---|
| 1–9, 0 (top row or numpad) | Load configuration file 1–10 |
| Up / Down | Iterations +1 / −1 |
| Left / Right | Angle −1° / +1° |
| Shift + Up / Down | Random seed +1 / −1 |
| Shift + Left / Right | Branch length ratio −0.05 / +0.05 |
| Right mouse drag, wheel | Rotate the view, zoom |

The menu on the left has the same controls, a rule editor (Apply rules / Reload file) and a tick box for
3D branches and leaves. The icon buttons next to it quit, change the background colour and lock the camera
rotation. Hotkeys are switched off while the cursor is in a text box.

## Files

| Path | Contents |
|---|---|
| `Assets/Scripts/MyRewriter.cs` | Rule class; parallel (and stochastic) rewriting |
| `Assets/Scripts/MyTurtle.cs` | 3D turtle with a quaternion and a stack; returns segments and leaves |
| `Assets/Scripts/MyLSystem.cs` | Loads files, hotkeys, menu, builds the line or 3D mesh |
| `Assets/Scripts/MyCamera.cs` | Frames the model, orbit camera, rotation lock |
| `Assets/Scripts/MyButtons.cs` | Quit, background colour and lock buttons |
| `Assets/StreamingAssets/LSystems/*.txt` | The ten L-systems (`key=value`, `rule=F:F[+F]F`, `rule=F:0.33:F[+F]F`) |
| `Report/` | Report PDF, the figures (output images) and the Python scripts that build the PDF |

Files 1–6 are Figure 1.24 a–f of Prusinkiewicz & Lindenmayer, *The Algorithmic Beauty of Plants* (1990).
