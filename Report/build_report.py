"""Builds the CW1 report PDF for the LSystemTree project.

Usage:  python build_report.py figures YouzhiLi-L-system-2026.pdf
If figures/ui.png exists (a screenshot taken with the menu's Screenshot button), it is added as a figure.
"""
import os
import re
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate, PageBreak,
                                PageTemplate, Paragraph, Preformatted, Spacer, Table, TableStyle)

FIG, OUT = sys.argv[1], sys.argv[2]

# ---------------------------------------------------------------- check these before submitting
AUTHOR = "Youzhi Li"
MODULE = "Mathematics and Graphics for Computer Games 1"
PROGRAMME = "MSc Computer Game Programming"
INSTITUTION = "Goldsmiths, University of London"
DATE = "23 / 11 / 2026"
VIDEO_URL = "[add your YouTube link here]"
RUNNING_HEAD = "L-SYSTEM PLANT GENERATOR"

# ---------------------------------------------------------------- fonts and styles
F = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Serif", os.path.join(F, "times.ttf")))
pdfmetrics.registerFont(TTFont("Serif-Bold", os.path.join(F, "timesbd.ttf")))
pdfmetrics.registerFont(TTFont("Serif-Italic", os.path.join(F, "timesi.ttf")))
pdfmetrics.registerFont(TTFont("Serif-BoldItalic", os.path.join(F, "timesbi.ttf")))
pdfmetrics.registerFont(TTFont("Mono", os.path.join(F, "consola.ttf")))
pdfmetrics.registerFontFamily("Serif", normal="Serif", bold="Serif-Bold", italic="Serif-Italic",
                              boldItalic="Serif-BoldItalic")

body = ParagraphStyle("body", fontName="Serif", fontSize=12, leading=20, alignment=TA_JUSTIFY,
                      firstLineIndent=1.27 * cm)
body_ni = ParagraphStyle("bodyni", parent=body, firstLineIndent=0)
h1 = ParagraphStyle("h1", fontName="Serif-Bold", fontSize=13, leading=20, alignment=TA_CENTER,
                    spaceBefore=12, spaceAfter=6, keepWithNext=True)
h2 = ParagraphStyle("h2", fontName="Serif-Bold", fontSize=12, leading=20, spaceBefore=8, spaceAfter=2,
                    keepWithNext=True)
caption = ParagraphStyle("cap", fontName="Serif-Italic", fontSize=10.5, leading=13, spaceBefore=3, spaceAfter=10)
small = ParagraphStyle("small", fontName="Serif", fontSize=10, leading=12.5, alignment=TA_CENTER)
cell = ParagraphStyle("cell", fontName="Serif", fontSize=10, leading=12.5)
cellmono = ParagraphStyle("cellmono", fontName="Mono", fontSize=8.5, leading=11)
code = ParagraphStyle("code", fontName="Mono", fontSize=8.5, leading=11, backColor=colors.HexColor("#f4f5f2"),
                      borderColor=colors.HexColor("#d0d4cc"), borderWidth=0.5, borderPadding=6, leftIndent=6,
                      rightIndent=6, spaceBefore=6, spaceAfter=4)
ref = ParagraphStyle("ref", parent=body, firstLineIndent=-1.27 * cm, leftIndent=1.27 * cm, alignment=TA_LEFT,
                     spaceAfter=4)
title_s = ParagraphStyle("title", fontName="Serif", fontSize=12, leading=24, alignment=TA_CENTER)
title_b = ParagraphStyle("titleb", parent=title_s, fontName="Serif-Bold", fontSize=15, leading=26)

W, H = A4
MARGIN = 2.54 * cm
TEXT_W = W - 2 * MARGIN
words = [0]
fig_no = [0]
tab_no = [0]


def P(text, style=body):
    plain = re.sub(r"<[^>]+>", " ", text)
    plain = re.sub(r"&\w+;", " ", plain)
    words[0] += len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.\-]*", plain))
    return Paragraph(text, style)


def M(t):
    return f"<font name='Mono' size='10'>{t}</font>"


def figure(paths, cap, labels=None, max_h=None):
    fig_no[0] += 1
    n = len(paths)
    w = (TEXT_W - 0.25 * cm * (n - 1)) / n
    cells = []
    for p in paths:
        img = Image(os.path.join(FIG, p))
        ratio = img.imageHeight / img.imageWidth
        dw, dh = w, w * ratio
        if max_h and dh > max_h:
            dh, dw = max_h, max_h / ratio
        cells.append(Image(os.path.join(FIG, p), width=dw, height=dh))
    rows = [cells]
    if labels:
        rows.append([Paragraph(t, small) for t in labels])
    t = Table(rows, colWidths=[TEXT_W / n] * n)
    t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                           ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return KeepTogether([t, Paragraph(f"<font name='Serif-BoldItalic'>Figure {fig_no[0]}</font> {cap}", caption)])


def table(data, widths, mono_cols=()):
    rows = []
    for r, row in enumerate(data):
        rows.append([Paragraph(f"<b>{v}</b>" if r == 0 else v, cellmono if (c in mono_cols and r) else cell)
                     for c, v in enumerate(row)])
    t = Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black),
                           ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
                           ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


def table_caption(text):
    tab_no[0] += 1
    return Paragraph(f"<font name='Serif-Bold'>Table {tab_no[0]}</font><br/><i>{text}</i>",
                     ParagraphStyle("tc", parent=caption, fontName="Serif", spaceBefore=8, spaceAfter=4,
                                    keepWithNext=True))


def pipeline():
    d = Drawing(TEXT_W, 100)
    boxes = [("Text file", "StreamingAssets"), ("MyLSystem", "LoadFile()"), ("MyRewriter", "Generate()"),
             ("MyTurtle", "Draw()"), ("MyLSystem", "BuildMesh()")]
    gap = 14
    bw, bh, y = (TEXT_W - 4 * gap) / 5, 50, 36
    for i, (a, b) in enumerate(boxes):
        x = i * (bw + gap)
        d.add(Rect(x, y, bw, bh, rx=5, ry=5, fillColor=colors.HexColor("#eef3ea"),
                   strokeColor=colors.HexColor("#5a6a55"), strokeWidth=0.8))
        d.add(String(x + bw / 2, y + 29, a, fontName="Serif-Bold", fontSize=10, textAnchor="middle"))
        d.add(String(x + bw / 2, y + 14, b, fontName="Mono", fontSize=8, textAnchor="middle"))
        if i < 4:
            ax = x + bw + 1
            d.add(Line(ax, y + bh / 2, ax + gap - 4, y + bh / 2, strokeColor=colors.HexColor("#5a6a55")))
            d.add(Polygon([ax + gap - 2, y + bh / 2, ax + gap - 7, y + bh / 2 + 3, ax + gap - 7, y + bh / 2 - 3],
                          fillColor=colors.HexColor("#5a6a55"), strokeColor=None))
    d.add(String(TEXT_W / 2, 12, "axiom, rules, n, angle  →  string of symbols  →  list of line segments  →  one Mesh",
                 fontName="Serif-Italic", fontSize=9.5, textAnchor="middle"))
    return d


HAS_UI = os.path.exists(os.path.join(FIG, "ui.png"))
FN = {}
for _i, _k in enumerate(["ui"] * HAS_UI + ["pipe", "plants", "iter", "angle", "seed", "tree", "bush", "solid"], 1):
    FN[_k] = _i

ST = {}
for line in open(os.path.join(FIG, "stats.txt"), encoding="utf-8"):
    parts = line.rstrip("\n").split("\t")
    ST[parts[0]] = dict(p.split("=", 1) for p in parts[2:])
    ST[parts[0]]["title"] = parts[1]


def fmt(n):
    return f"{int(n):,}"


def title_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Serif", 12)
    canvas.drawString(MARGIN, H - 1.5 * cm, f"Running head: {RUNNING_HEAD}")
    canvas.drawRightString(W - MARGIN, H - 1.5 * cm, str(doc.page))
    canvas.restoreState()


def other_pages(canvas, doc):
    canvas.saveState()
    canvas.setFont("Serif", 12)
    canvas.drawString(MARGIN, H - 1.5 * cm, RUNNING_HEAD)
    canvas.drawRightString(W - MARGIN, H - 1.5 * cm, str(doc.page))
    canvas.restoreState()


doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN,
                      bottomMargin=MARGIN, title="YouzhiLi-L-system-2026", author=AUTHOR,
                      subject="Coursework 1: L-Systems")
frame = Frame(MARGIN, MARGIN, TEXT_W, H - 2 * MARGIN, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate("title", [frame], onPage=title_page),
                      PageTemplate("body", [frame], onPage=other_pages)])
story = []

# ---------------------------------------------------------------- title page
story += [Spacer(1, 2 * cm), Paragraph("Lindenmayer Systems:", title_b),
          Paragraph("A Simple 2D and 3D L-System Plant Generator in Unity", title_b), Spacer(1, 0.5 * cm)]
cw = TEXT_W * 0.55
story += [Image(os.path.join(FIG, "09.png"), width=cw, height=cw, kind="proportional"), Spacer(1, 0.6 * cm)]
for t in [AUTHOR, MODULE, PROGRAMME, INSTITUTION, "Coursework 1: L-Systems", DATE]:
    story.append(Paragraph(t, title_s))
story += [NextPageTemplate("body"), PageBreak()]

# ---------------------------------------------------------------- abstract
story.append(Paragraph("Abstract", h1))
story.append(P(
    "This report describes a small L-system program that I wrote in Unity with C#. The program reads "
    "L-system definitions from plain text files, rewrites the axiom with the production rules, and draws the "
    "result with a turtle. Ten files can be loaded with the number keys: the six plants of Figure 1.24 in "
    "<i>The Algorithmic Beauty of Plants</i>, a stochastic plant, a 3D bush, a 3D tree and the dragon curve. "
    "The arrow keys step through the iterations and change the branching angle, and with Shift they change the "
    "branch length ratio and the random seed. A menu offers the same controls with the mouse and a rule editor "
    "for trying new L-systems in Play mode. As extra features the turtle works in 3D using quaternions, "
    "rules can be stochastic, the plant can be drawn as lines or as 3D branches with leaves, and an orbit camera lets the user "
    "look at the 3D models from any side.", body_ni))
story.append(Spacer(1, 6))
story.append(Paragraph("<i>Keywords:</i> Lindenmayer systems, turtle graphics, procedural plants, Unity, C#", body_ni))
story.append(PageBreak())

# ---------------------------------------------------------------- introduction
story.append(Paragraph("Lindenmayer Systems:<br/>A Simple 2D and 3D L-System Plant Generator in Unity", h1))
story.append(Paragraph("Introduction and Objectives", h1))
story.append(P(
    "An L-system is a string-rewriting system introduced by the biologist Aristid Lindenmayer to model the "
    "growth of simple organisms (Lindenmayer, 1968). It has three parts: an alphabet of symbols, a starting "
    "string called the <i>axiom</i>, and a set of <i>production rules</i> that say what each symbol turns into. "
    "In each derivation step every symbol in the string is replaced at the same time. For example, with the "
    "axiom A and the rules A → AB and B → A, the first generations are A, AB, ABA, ABAAB and ABAABABA. "
    "Their lengths 1, 2, 3, 5, 8 are the Fibonacci numbers."))
story.append(P(
    "On its own an L-system only produces strings. Prusinkiewicz (1986) showed that the strings become "
    "pictures of plants when each symbol is read as a command for a turtle, a drawing cursor in the style of "
    "LOGO (Abelson &amp; diSessa, 1981): F means move forward and draw, + and − mean turn, and the brackets "
    "[ and ] save and restore the turtle so that a branch can grow and the turtle can then return to the stem. "
    "These ideas are explained in detail in <i>The Algorithmic Beauty of Plants</i> (Prusinkiewicz &amp; "
    "Lindenmayer, 1990), which I used as my main reference."))
story.append(P(
    "My objectives followed the coursework brief: read L-system parameters from configuration files, display "
    "the model, step through the iterations with hotkeys, load at least eight different files with hotkeys "
    "(six of them the plants in Figure 1.24 of the book), and change at least three parameters with hotkeys. "
    "I also wanted to try two of the suggested extra features, 3D and stochastic L-systems, while keeping the "
    "code short enough that I could explain every line of it."))

# ---------------------------------------------------------------- features
story.append(Paragraph("Features", h1))
story.append(Paragraph("Configuration Files", h2))
story.append(P(
    f"Each L-system is stored in its own text file in {M('Assets/StreamingAssets/LSystems')}. I chose a simple "
    f"key=value format so that the files are easy to read and edit by hand. Lines starting with # are comments, "
    f"which I use to note where each L-system comes from. A rule is written as {M('symbol:successor')}, or as "
    f"{M('symbol:probability:successor')} for a stochastic rule. The optional {M('ratio')} key sets how much "
    f"shorter each branch is than its parent. Listing 1 shows the file for Plant D, and Table 1 lists all ten files."))
story.append(KeepTogether([Preformatted(
    "# Prusinkiewicz & Lindenmayer (1990), Fig. 1.24d (node rewriting)\n"
    "name=Plant D\n"
    "axiom=X\n"
    "rule=X:F[+X]F[-X]+X\n"
    "rule=F:FF\n"
    "iterations=7\n"
    "angle=20", code),
    Paragraph("<font name='Serif-BoldItalic'>Listing 1</font> <i>The configuration file 04_PlantD.txt.</i>", caption)]))

rows = [["Key", "File", "Axiom and rules", "n", "δ"],
        ["1", "Plant A", "F<br/>F → F[+F]F[-F]F", "5", "25.7°"],
        ["2", "Plant B", "F<br/>F → F[+F]F[-F][F]", "5", "20°"],
        ["3", "Plant C", "F<br/>F → FF-[-F+F+F]+[+F-F-F]", "4", "22.5°"],
        ["4", "Plant D", "X<br/>X → F[+X]F[-X]+X, F → FF", "7", "20°"],
        ["5", "Plant E", "X<br/>X → F[+X][-X]FX, F → FF", "7", "25.7°"],
        ["6", "Plant F", "X<br/>X → F-[[X]+X]+F[+FX]-X, F → FF", "5", "22.5°"],
        ["7", "Stochastic plant", "F<br/>F →(0.33) F[+F]F[-F]F<br/>F →(0.33) F[+F]F<br/>F →(0.34) F[-F]F", "5", "25.7°"],
        ["8", "3D bush", "A<br/>A → [&amp;FL!A]/////[&amp;FL!A]///////[&amp;FL!A]<br/>F → S/////F, S → FL", "7", "22.5°"],
        ["9", "3D tree", "FFA<br/>A → F[&amp;&amp;FA]/////[&amp;&amp;FA]///////[&amp;&amp;FA]FA", "5", "20°"],
        ["0", "Dragon curve", "FX<br/>X → X+YF+, Y → -FX-Y", "10", "90°"]]
story.append(table_caption("The ten configuration files"))
story.append(table(rows, [1.1 * cm, 3.4 * cm, 9.2 * cm, 0.9 * cm, 1.4 * cm], mono_cols=(2,)))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "<i>Note.</i> Files 1–6 are Figure 1.24 a–f of Prusinkiewicz and Lindenmayer (1990). File 7 is their "
    "stochastic example (section 1.7), file 8 uses productions p1–p3 of their Figure 1.25 without the leaves, "
    "file 9 is my own variation of the branching pattern in their Figure 2.8 (with a length ratio of 0.65), and "
    "file 10 is the Heighway dragon from Bourke (1991).", ParagraphStyle("note", parent=cell, spaceAfter=10)))

story.append(Paragraph("Hotkeys", h2))
story.append(P(
    "The hotkeys use only the arrow keys and the number keys (Table 2), so that the letter keys are free for "
    "typing rules in the menu. The up and down arrows change the number of iterations, so the user can watch "
    "the plant develop one derivation step at a time. Four parameters can be changed with hotkeys: the "
    "iterations, the branching angle, the branch length ratio and the random seed. While the cursor is in a "
    "text box the hotkeys are switched off, so typing a digit does not load a file. After every change the "
    "whole model is rebuilt from the axiom. To stop the program "
    "from freezing, the iterations are limited to 12 and the string to one million symbols; if a change would "
    "go over the limit, the program goes back one iteration and shows a message."))
keys = [["Key", "Action", "Key", "Action"],
        ["1–9, 0", "Load file 1–10 (also numpad)", "↑ / ↓", "Iterations +1 / −1"],
        ["← / →", "Angle −1° / +1°", "Shift + ↑ / ↓", "Random seed +1 / −1"],
        ["Shift + ← / →", "Length ratio −0.05 / +0.05", "Right drag", "Rotate the camera"],
        ["Wheel", "Zoom", "", ""]]
story.append(table_caption("Hotkeys"))
story.append(table(keys, [2.6 * cm, 5.4 * cm, 2.6 * cm, 5.4 * cm]))
story.append(Spacer(1, 8))
story.append(P(
    "A menu on the left of the screen, made with Unity's immediate-mode GUI (OnGUI and GUILayout), shows the "
    "current file and gives the same controls with the mouse: buttons for the previous and next file, sliders "
    "for the iterations, the angle and the length ratio, a button for a new random seed, and buttons for "
    "automatic rotation, a screenshot and hiding the menu. It also shows the number of symbols and lines and "
    "a list of the hotkeys."))
story.append(P(
    "<b>Rule editor.</b> The menu has a text box for the axiom and a larger one for the rules, written one "
    f"per line in the same format as the files ({M('F:F[+F]F')} or {M('F:0.5:F[+F]')}). When a file is loaded, "
    "its axiom and rules are copied into the boxes. Pressing Apply rules reads the boxes with the same function "
    "that reads the files and rebuilds the model, so a new L-system can be tried without leaving Play mode. If "
    "a line cannot be read, nothing is changed and the menu shows which line is wrong. Reload file goes back "
    "to the rules in the file."))
if os.path.exists(os.path.join(FIG, "ui.png")):
    story.append(figure(["ui.png"], "The program running, with the menu and rule editor on the left."))

story.append(Paragraph("Extra Features", h2))
story.append(P(
    "<b>3D turtle.</b> The turtle stores its orientation as a quaternion instead of a single angle. Besides "
    "+ and −, it understands &amp; and ^ (pitch down and up), \\ and / (roll left and right) and | (turn around), "
    "which are the 3D commands described in section 1.5 of the book. Because + and − rotate around the Z axis, "
    "the 2D plants stay flat in the XY plane and are drawn by exactly the same code as the 3D ones."))
story.append(P(
    "<b>Stochastic rules.</b> When a symbol has several rules, one of them is chosen at random each time the "
    "symbol is rewritten, with a chance proportional to its probability (Prusinkiewicz &amp; Lindenmayer, "
    f"1990, section 1.7). The random numbers come from a generator created with the file's seed, so the same "
    f"seed always gives the same plant, and changing the seed (Shift + ↑ / ↓ or the New seed button) gives a new plant of the same kind (Figure {FN['seed']})."))
story.append(P(
    "<b>Branch length ratio and colour.</b> Each [ multiplies the step length by the ratio, so side branches "
    f"are shorter than the stem they grow from (Figure {FN['angle']}). Every line also stores how many brackets deep it is, "
    "and its colour goes from brown at the trunk to green at the tips."))
story.append(P(
    "<b>3D branches and leaves.</b> A tick box in the menu switches from lines to a solid model. Each segment "
    "becomes a six-sided tube. To build it, two directions at right angles to the segment are found with the "
    "cross product, and six points are placed around the start and the end of the segment with cos and sin "
    "of the angle, like points on a circle; neighbouring points are joined by two triangles. The radius is "
    "r = r<sub>0</sub> · 0.7<sup><i>d</i></sup>, where <i>d</i> is the bracket depth, so every branch level is thinner than the one "
    "it grows from. A leaf is added at every ] (the tip of a branch) and at every L. It is a diamond made of "
    "two triangles whose corners are written in the turtle's own frame and turned with the turtle's quaternion, "
    "so the leaf points the same way as its branch. The trunk radius and the leaf length are a percentage of "
    "the size of the plant, so the same settings suit a small and a large model. Branches and leaves are two "
    "sub-meshes of one mesh, with a brown and a green material that are lit by the scene's light "
    f"(Figure {FN['solid']})."))
story.append(P(
    "<b>Orbit camera.</b> After each rebuild the camera is moved so that the whole model fits on the screen. "
    "Holding the right mouse button rotates the camera around the model, and the wheel zooms."))
story.append(P(
    "<b>Icon buttons.</b> A column of three buttons with icons sits next to the menu: one quits the program "
    "(in the editor it stops Play mode), one cycles the background through light grey, dark and sky blue, and "
    "one locks the camera rotation so that the view cannot be turned by accident while the parameters are "
    "changed; the padlock icon shows whether the lock is on. Hovering over a button shows its name. The "
    "buttons are in a separate short script, MyButtons, and the icons are loaded from a Resources folder."))

# ---------------------------------------------------------------- data classes
story.append(Paragraph("Data Classes and Structures", h1))
story.append(P(
    "The program has five scripts. MyLSystem is the MonoBehaviour that is placed in the scene, and it adds "
    "MyCamera and MyButtons when the program starts; the other two hold the L-system logic and do not depend "
    "on the scene."))
classes = [["Script", "Contents", "Purpose"],
           ["MyRewriter.cs", "class Rule, static class MyRewriter", "Stores one rule; rewrites the axiom n times"],
           ["MyTurtle.cs", "struct Segment, static class MyTurtle", "Reads the string and returns the line segments"],
           ["MyLSystem.cs", "class MyLSystem : MonoBehaviour", "Loads files, hotkeys, menu, builds the mesh"],
           ["MyCamera.cs", "class MyCamera : MonoBehaviour", "Frames the model, orbits around it, rotation lock"],
           ["MyButtons.cs", "class MyButtons : MonoBehaviour", "Quit, background colour and lock buttons"]]
story.append(table_caption("The five scripts"))
story.append(table(classes, [3.2 * cm, 6.0 * cm, 6.7 * cm], mono_cols=(0, 1)))
story.append(Spacer(1, 8))
story.append(Paragraph("Rule", h2))
story.append(P(
    f"A {M('Rule')} has three fields: the symbol on the left ({M('char')}), the successor string on the right, "
    f"and a probability. The rules of the current L-system are kept in a {M('List&lt;Rule&gt;')}. I used a list "
    f"instead of a dictionary because one symbol can have several rules in a stochastic L-system."))
story.append(Paragraph("Turtle State and Stack", h2))
story.append(P(
    f"The turtle's state is a small struct with its position ({M('Vector3')}), orientation "
    f"({M('Quaternion')}), current step length and bracket depth. The brackets use a {M('Stack&lt;State&gt;')}: "
    f"[ pushes a copy of the state and ] pops it. A stack is the right structure because branches are nested; "
    f"the last branch that was opened is always the first one to be closed. Because the state is a struct, "
    f"the stack stores a copy, so turning inside a branch cannot change the saved state of the stem."))
story.append(Paragraph("Segment and Mesh", h2))
story.append(P(
    f"Every F produces a {M('Segment')} with a start point, an end point and a depth. MyLSystem then puts all "
    f"segments into one Unity {M('Mesh')} drawn with {M('MeshTopology.Lines')}: two vertices and two indices "
    f"per segment, plus a vertex colour. Using a single mesh means that even Plant C, with 4,096 lines, is "
    f"drawn in one draw call. The mesh uses 32-bit indices so that the larger models do not exceed the 65,535 "
    f"vertex limit of 16-bit indices."))

# ---------------------------------------------------------------- main structure
story.append(Paragraph("Main Structure", h1))
fig_no[0] += 1
story.append(KeepTogether([pipeline(), Paragraph(
    f"<font name='Serif-BoldItalic'>Figure {fig_no[0]}</font> What happens when a file is loaded or a parameter changes.",
    caption)]))
steps = [
    f"<b>Start-up.</b> {M('Init()')} creates the mesh and the material, adds the camera script and lists the "
    f"text files in alphabetical order. The first file is then loaded.",
    f"<b>Loading.</b> {M('LoadFile()')} reads the file line by line, splits each line at the first = sign and "
    f"stores the value in the matching field. Numbers are parsed with the invariant culture, so 25.7 is read "
    f"correctly on computers set to languages that use a decimal comma.",
    f"<b>Rewriting.</b> {M('MyRewriter.Generate()')} repeats the rewriting n times. In each iteration it "
    f"reads the current string and writes the result into a new {M('StringBuilder')}, so all symbols are "
    f"replaced in parallel and new symbols are only rewritten in the next iteration.",
    f"<b>Turtle.</b> {M('MyTurtle.Draw()')} goes through the string once. F moves the turtle by "
    f"{M('rotation * Vector3.up * length')} and records a segment; the rotation symbols multiply the "
    f"quaternion by {M('Quaternion.Euler(...)')}; the brackets push and pop the stack.",
    f"<b>Mesh and camera.</b> {M('BuildMesh()')} fills the mesh and {M('MyCamera.Frame()')} places the camera "
    f"at a distance d = r / sin(θ/2), where r is the radius of the model's bounding sphere and θ the camera's "
    f"field of view. At this distance the whole sphere fits in the view.",
    f"<b>Hotkeys and menu.</b> {M('Update()')} checks the keys every frame and {M('OnGUI()')} draws the menu. "
    f"If a key, a slider or the rule editor changed something, they call {M('Rebuild()')}, which runs steps 3–5 again.",
]
for s in steps:
    story.append(P(s, ParagraphStyle("st", parent=body, firstLineIndent=0, leftIndent=0.5 * cm, spaceAfter=3)))
story.append(P(
    "One detail I had to get right is the order of the quaternion multiplication. Writing "
    f"{M('rotation = rotation * turn')} applies the turn around the turtle's own axes, which is what the "
    "L-system symbols mean (for example, &amp; pitches the branch down relative to where the turtle is "
    f"pointing). Writing {M('turn * rotation')} would rotate around the world axes instead, and the 3D "
    "models would come out wrong."))

# ---------------------------------------------------------------- results
story.append(Paragraph("Results", h1))
story.append(P(
    f"All the pictures in this section were rendered by the program from the configuration files. Figure {FN['plants']} "
    "shows the six required plants; their shapes match Figure 1.24 a–f of the book."))
two_d = ["01", "02", "03", "04", "05", "06"]
labels = [f"<b>{'abcdef'[i]}</b>  n = {ST[k]['n']}, δ = {float(ST[k]['angle']):g}°" for i, k in enumerate(two_d)]
fig_no[0] += 1
grid = []
for r0 in (0, 3):
    grid.append([Image(os.path.join(FIG, k + ".png"), width=TEXT_W / 3 - 0.3 * cm, height=TEXT_W / 3 - 0.3 * cm)
                 for k in two_d[r0:r0 + 3]])
    grid.append([Paragraph(t, small) for t in labels[r0:r0 + 3]])
gt = Table(grid, colWidths=[TEXT_W / 3] * 3)
gt.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 1),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
story.append(KeepTogether([gt, Paragraph(
    f"<font name='Serif-BoldItalic'>Figure {fig_no[0]}</font> Files 1–6: the six plants of Figure 1.24 a–f in "
    "Prusinkiewicz and Lindenmayer (1990), drawn by the program.", caption)]))

story.append(P(
    f"Figure {FN['iter']} shows Plant A after one to five iterations. Each F becomes five F symbols, so the number of "
    "lines is 5<super>n</super>: " + ", ".join(fmt(ST[f"iterA_{n}"]["segments"]) for n in range(1, 6)) +
    ". The length of the whole string grows in the same way: " +
    ", ".join(fmt(ST[f"iterA_{n}"]["symbols"]) for n in range(1, 6)) +
    " symbols, which is (5<super>n+1</super> − 3) / 2."))
story.append(figure([f"iterA_{n}.png" for n in range(1, 6)], "Plant A after 1 to 5 iterations (up arrow).",
                    labels=[f"n = {n}" for n in range(1, 6)]))
story.append(P(
    f"Figure {FN['angle']} shows the effect of the angle and length ratio hotkeys. The grammar stays the same, but a "
    "smaller angle gives a narrow plant and a larger angle a wide one; a smaller ratio makes the side branches "
    "shorter, so the plant looks more like a tree with a clear main stem."))
story.append(figure(["angleE_15.png", "angleE_25.7.png", "angleE_40.png", "ratioD_1.0.png", "ratioD_0.8.png",
                     "ratioD_0.6.png"],
                    "Left: Plant E with angle 15°, 25.7° and 40° (arrow keys). Right: Plant D with length ratio "
                    "1.0, 0.8 and 0.6 (Shift + ← / →).",
                    labels=["15°", "25.7°", "40°", "1.0", "0.8", "0.6"]))
story.append(P(
    f"Figure {FN['seed']} shows four seeds of the stochastic plant. They all use the same three rules, but because a "
    "different rule is chosen at different places, each plant has its own shape and size (between " +
    f"{min(int(ST[f'seed_{s}']['segments']) for s in (1, 2, 3, 4))} and "
    f"{max(int(ST[f'seed_{s}']['segments']) for s in (1, 2, 3, 4))} lines)."))
story.append(figure([f"seed_{s}.png" for s in (1, 2, 3, 4)], "File 7, the stochastic plant, with seeds 1 to 4 (Shift + ↑).",
                    labels=[f"seed {s}" for s in (1, 2, 3, 4)]))
story.append(P(
    f"Figures {FN['tree']} and {FN['bush']} show the 3D models. The 3D tree has a main trunk with three side branches at every node, "
    "turned around the trunk by the roll symbols, so from above the branches spread in all directions."))
story.append(figure(["iter3d_2.png", "iter3d_4.png", "09.png", "tree3d_top.png"],
                    "File 9, the 3D tree, after 2, 4 and 5 iterations, and seen from above.",
                    labels=["n = 2", "n = 4", "n = 5", "top view"]))
story.append(figure(["08.png", "10.png"], "File 8, the 3D bush, and file 10, the dragon curve.",
                    labels=["3D bush", "Dragon curve"], max_h=7 * cm))

story.append(figure(["solid_A.png", "solid_E.png", "solid_tree.png", "solid_bush.png"],
                    "The same L-systems drawn with 3D branches and leaves: Plant A, Plant E, the 3D tree and the 3D bush.",
                    labels=["Plant A", "Plant E", "3D tree", "3D bush"], max_h=6.5 * cm))

sizes = [["File", "n", "Symbols", "Lines"]]
for k in ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]:
    sizes.append([ST[k]["title"], ST[k]["n"], fmt(ST[k]["symbols"]), fmt(ST[k]["segments"])])
story.append(P(
    "Table 4 lists the size of each model at its default number of iterations. The largest, the 3D bush, has "
    "about 47,000 symbols and 3,900 lines, and all of them rebuild without a noticeable pause."))
story.append(table_caption("Size of each model"))
story.append(table(sizes, [5.5 * cm, 1.5 * cm, 4.0 * cm, 4.0 * cm]))
story.append(Spacer(1, 6))

# ---------------------------------------------------------------- conclusion
story.append(Paragraph("Conclusion", h1))
story.append(P(
    "The program does what the brief asks for. It reads ten configuration files, each loaded with its own key; "
    "it draws the six required plants correctly; the iterations can be stepped with the arrow keys; and four "
    "parameters can be changed with hotkeys. I also added a menu with a rule editor, a 3D turtle, 3D branches with leaves, stochastic rules, a branch length ratio, "
    "colouring by depth and an orbit camera. Keeping the rewriting, the turtle and the drawing in separate "
    "scripts made the program easier to write and test, because I could check the strings in the console "
    "before I worked on the drawing."))
story.append(P(
    "The program has some clear limits. The 3D branches are separate tubes, so small gaps can be seen where "
    "two branches meet at a large angle, and the leaves are flat and all the same shape. The L-systems are context-free and not "
    "parametric, so effects such as signals moving through the plant (context-sensitive L-systems, section 1.8 "
    "of the book) or branches whose length depends on their age (parametric L-systems, section 1.10) cannot "
    "be expressed. Tropism, which bends branches towards gravity or light (section 2.2), would also "
    "make the 3D trees more realistic. Interactive tools such as TreeSketch (Longay et al., 2012) show how far "
    "these ideas can be taken."))
story.append(P(f"A video demonstration of the program is available at {VIDEO_URL}."))
story.append(Spacer(1, 8))
wc_pos = len(story)
story.append(Paragraph("", body_ni))

# ---------------------------------------------------------------- references
story.append(PageBreak())
story.append(Paragraph("References", h1))
for r in [
    "Abelson, H., &amp; diSessa, A. A. (1981). <i>Turtle geometry: The computer as a medium for exploring "
    "mathematics</i>. MIT Press.",
    "Bourke, P. (1991). <i>L-system user notes</i>. Retrieved from http://paulbourke.net/fractals/lsys/",
    "Lindenmayer, A. (1968). Mathematical models for cellular interactions in development, Parts I and II. "
    "<i>Journal of Theoretical Biology, 18</i>(3), 280–315.",
    "Longay, S., Runions, A., Boudon, F., &amp; Prusinkiewicz, P. (2012). TreeSketch: Interactive procedural "
    "modeling of trees on a tablet. In <i>Proceedings of the International Symposium on Sketch-Based Interfaces "
    "and Modeling</i> (pp. 107–120). Eurographics Association.",
    "Prusinkiewicz, P. (1986). Graphical applications of L-systems. In <i>Proceedings of Graphics Interface '86</i> "
    "(pp. 247–253). Canadian Information Processing Society.",
    "Prusinkiewicz, P., &amp; Lindenmayer, A. (1990). <i>The algorithmic beauty of plants</i>. Springer-Verlag. "
    "Electronic version (2004) retrieved from http://algorithmicbotany.org/papers/#abop",
    "Unity Technologies. (2025). <i>Unity scripting API: Mesh</i>. Retrieved from "
    "https://docs.unity3d.com/ScriptReference/Mesh.html",
]:
    story.append(Paragraph(r, ref))

story[wc_pos] = Paragraph(f"<i>Word count (abstract to conclusion, excluding tables, listings, captions and "
                          f"references): {words[0]:,}</i>", body_ni)
doc.build(story)
print("words:", words[0])
