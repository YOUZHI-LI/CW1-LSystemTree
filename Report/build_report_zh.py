"""中文版报告。与 build_report.py（英文版）逐段对应：改一份时，同一段落也要改另一份。

用法:  python build_report_zh.py figures YouzhiLi-L-system-2026-CN.pdf
（或者运行 python build_all.py，同时生成中英文两份。）
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

# 封面信息与视频链接从英文版读取，只需在 build_report.py 里改一次
_en = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_report.py"), encoding="utf-8").read()


def _setting(name):
    return re.search(rf'^{name} = "(.*)"', _en, re.M).group(1)


AUTHOR = _setting("AUTHOR")
MODULE = _setting("MODULE")
PROGRAMME = _setting("PROGRAMME")
INSTITUTION = _setting("INSTITUTION")
DATE = _setting("DATE")
VIDEO_URL = _setting("VIDEO_URL")
if VIDEO_URL.startswith("[add"):
    VIDEO_URL = "[在此填写 YouTube 链接]"
RUNNING_HEAD = "L-系统植物生成器"

# ---------------------------------------------------------------- fonts and styles
F = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Song", os.path.join(F, "simsun.ttc"), subfontIndex=0))
pdfmetrics.registerFont(TTFont("Hei", os.path.join(F, "simhei.ttf")))
pdfmetrics.registerFont(TTFont("Kai", os.path.join(F, "simkai.ttf")))
pdfmetrics.registerFont(TTFont("Mono", os.path.join(F, "consola.ttf")))
# <b> 用黑体，<i> 用楷体
pdfmetrics.registerFontFamily("Song", normal="Song", bold="Hei", italic="Kai", boldItalic="Hei")
pdfmetrics.registerFontFamily("Kai", normal="Kai", bold="Hei", italic="Kai", boldItalic="Hei")
pdfmetrics.registerFontFamily("Hei", normal="Hei", bold="Hei", italic="Hei", boldItalic="Hei")

body = ParagraphStyle("body", fontName="Song", fontSize=11.5, leading=21, alignment=TA_JUSTIFY,
                      firstLineIndent=23, wordWrap="CJK")
body_ni = ParagraphStyle("bodyni", parent=body, firstLineIndent=0)
h1 = ParagraphStyle("h1", fontName="Hei", fontSize=14, leading=22, alignment=TA_CENTER,
                    spaceBefore=12, spaceAfter=6, keepWithNext=True, wordWrap="CJK")
h2 = ParagraphStyle("h2", fontName="Hei", fontSize=12, leading=21, spaceBefore=8, spaceAfter=2,
                    keepWithNext=True, wordWrap="CJK")
caption = ParagraphStyle("cap", fontName="Kai", fontSize=10.5, leading=14, spaceBefore=3, spaceAfter=10,
                         wordWrap="CJK")
small = ParagraphStyle("small", fontName="Song", fontSize=10, leading=12.5, alignment=TA_CENTER, wordWrap="CJK")
cell = ParagraphStyle("cell", fontName="Song", fontSize=10, leading=13, wordWrap="CJK")
cellmono = ParagraphStyle("cellmono", fontName="Mono", fontSize=8.5, leading=11)
code = ParagraphStyle("code", fontName="Mono", fontSize=8.5, leading=11, backColor=colors.HexColor("#f4f5f2"),
                      borderColor=colors.HexColor("#d0d4cc"), borderWidth=0.5, borderPadding=6, leftIndent=6,
                      rightIndent=6, spaceBefore=6, spaceAfter=4)
ref = ParagraphStyle("ref", fontName="Times", fontSize=11.5, leading=20, firstLineIndent=-1.27 * cm,
                     leftIndent=1.27 * cm, alignment=TA_LEFT, spaceAfter=4)
title_s = ParagraphStyle("title", fontName="Song", fontSize=12, leading=24, alignment=TA_CENTER, wordWrap="CJK")
title_b = ParagraphStyle("titleb", parent=title_s, fontName="Hei", fontSize=16, leading=28)

pdfmetrics.registerFont(TTFont("Times", os.path.join(F, "times.ttf")))
pdfmetrics.registerFont(TTFont("Times-I", os.path.join(F, "timesi.ttf")))
pdfmetrics.registerFontFamily("Times", normal="Times", bold="Times", italic="Times-I", boldItalic="Times-I")

W, H = A4
MARGIN = 2.54 * cm
TEXT_W = W - 2 * MARGIN
chars = [0]
fig_no = [0]
tab_no = [0]


def fix(text):
    # 宋体没有数学减号 "−"，改用 Times 显示
    return text.replace("−", "<font name='Times'>−</font>")


def P(text, style=body):
    text = fix(text)
    plain = re.sub(r"<[^>]+>", " ", text)
    plain = re.sub(r"&\w+;", " ", plain)
    # 字数 = 汉字个数 + 英文单词/数字个数
    chars[0] += len(re.findall(r"[\u4e00-\u9fff]", plain))
    chars[0] += len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.\-]*", plain))
    return Paragraph(text, style)


def M(t):
    return f"<font name='Mono' size='9.5'>{t}</font>"


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
    return KeepTogether([t, Paragraph(f"<font name='Hei'>图 {fig_no[0]}</font>  {fix(cap)}", caption)])


def table(data, widths, mono_cols=()):
    rows = []
    for r, row in enumerate(data):
        rows.append([Paragraph(f"<b>{v}</b>" if r == 0 else fix(v), cellmono if (c in mono_cols and r) else cell)
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
    return Paragraph(f"<font name='Hei'>表 {tab_no[0]}</font><br/><font name='Kai'>{text}</font>",
                     ParagraphStyle("tc", parent=caption, fontName="Song", spaceBefore=8, spaceAfter=4,
                                    keepWithNext=True))


def pipeline():
    d = Drawing(TEXT_W, 100)
    boxes = [("文本文件", "StreamingAssets"), ("MyLSystem", "LoadFile()"), ("MyRewriter", "Generate()"),
             ("MyTurtle", "Draw()"), ("MyLSystem", "BuildMesh()")]
    gap = 14
    bw, bh, y = (TEXT_W - 4 * gap) / 5, 50, 36
    for i, (a, b) in enumerate(boxes):
        x = i * (bw + gap)
        d.add(Rect(x, y, bw, bh, rx=5, ry=5, fillColor=colors.HexColor("#eef3ea"),
                   strokeColor=colors.HexColor("#5a6a55"), strokeWidth=0.8))
        d.add(String(x + bw / 2, y + 29, a, fontName="Hei", fontSize=10, textAnchor="middle"))
        d.add(String(x + bw / 2, y + 14, b, fontName="Mono", fontSize=8, textAnchor="middle"))
        if i < 4:
            ax = x + bw + 1
            d.add(Line(ax, y + bh / 2, ax + gap - 4, y + bh / 2, strokeColor=colors.HexColor("#5a6a55")))
            d.add(Polygon([ax + gap - 2, y + bh / 2, ax + gap - 7, y + bh / 2 + 3, ax + gap - 7, y + bh / 2 - 3],
                          fillColor=colors.HexColor("#5a6a55"), strokeColor=None))
    d.add(String(TEXT_W / 2, 12, "公理、规则、n、角度  →  符号串  →  线段列表  →  一个 Mesh",
                 fontName="Kai", fontSize=9.5, textAnchor="middle"))
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

NAMES = {"01": "植物 A", "02": "植物 B", "03": "植物 C", "04": "植物 D", "05": "植物 E", "06": "植物 F",
         "07": "随机植物", "08": "3D 灌木", "09": "3D 树", "10": "龙形曲线"}


def fmt(n):
    return f"{int(n):,}"


def title_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Song", 11)
    canvas.drawString(MARGIN, H - 1.5 * cm, f"页眉：{RUNNING_HEAD}")
    canvas.drawRightString(W - MARGIN, H - 1.5 * cm, str(doc.page))
    canvas.restoreState()


def other_pages(canvas, doc):
    canvas.saveState()
    canvas.setFont("Song", 11)
    canvas.drawString(MARGIN, H - 1.5 * cm, RUNNING_HEAD)
    canvas.drawRightString(W - MARGIN, H - 1.5 * cm, str(doc.page))
    canvas.restoreState()


doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN,
                      bottomMargin=MARGIN, title="YouzhiLi-L-system-2026（中文版）", author=AUTHOR,
                      subject="Coursework 1: L-Systems")
frame = Frame(MARGIN, MARGIN, TEXT_W, H - 2 * MARGIN, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate("title", [frame], onPage=title_page),
                      PageTemplate("body", [frame], onPage=other_pages)])
story = []

# ---------------------------------------------------------------- title page
story += [Spacer(1, 2 * cm), Paragraph("Lindenmayer 系统：", title_b),
          Paragraph("在 Unity 中实现的简单 2D 与 3D L-系统植物生成器", title_b), Spacer(1, 0.5 * cm)]
cw = TEXT_W * 0.55
story += [Image(os.path.join(FIG, "09.png"), width=cw, height=cw, kind="proportional"), Spacer(1, 0.6 * cm)]
for t in [AUTHOR, MODULE, PROGRAMME.replace("&amp;", "&amp;"), INSTITUTION, "课程作业 1：L-系统（中文译本）", DATE]:
    story.append(Paragraph(t, title_s))
story += [NextPageTemplate("body"), PageBreak()]

# ---------------------------------------------------------------- abstract
story.append(Paragraph("摘要", h1))
story.append(P(
    "本报告介绍我用 C# 在 Unity 中编写的一个小型 L-系统程序。程序从纯文本文件中读取 L-系统的定义，"
    "用产生式规则对公理进行重写，再用海龟（turtle）把结果画出来。数字键可以加载十个文件：《植物的算法之美》"
    "（<i>The Algorithmic Beauty of Plants</i>）图 1.24 中的六种植物、一个随机植物、一个 3D 灌木、一棵 3D 树和龙形曲线。"
    "方向键用来逐步增减迭代次数和改变分枝角度，配合 Shift 键则改变分枝长度比例和随机种子。屏幕上的菜单提供同样的鼠标操作，"
    "还有一个规则编辑器，可以在 Play 模式下直接尝试新的 L-系统。额外功能包括：海龟用四元数在 3D 空间中工作；"
    "规则可以是随机的；植物可以画成线条，也可以画成带叶子的 3D 树枝；轨道相机可以从任意角度观察 3D 模型。", body_ni))
story.append(Spacer(1, 6))
story.append(Paragraph("<i>关键词：</i>Lindenmayer 系统，海龟绘图，程序化植物，Unity，C#", body_ni))
story.append(PageBreak())

# ---------------------------------------------------------------- introduction
story.append(Paragraph("Lindenmayer 系统：<br/>在 Unity 中实现的简单 2D 与 3D L-系统植物生成器", h1))
story.append(Paragraph("引言与目标", h1))
story.append(P(
    "L-系统是生物学家 Aristid Lindenmayer 为模拟简单生物的生长而提出的一种字符串重写系统（Lindenmayer, 1968）。"
    "它由三部分组成：一个符号字母表、一个称为<i>公理</i>的初始字符串，以及一组说明每个符号会变成什么的<i>产生式规则</i>。"
    "每一步推导中，字符串里的所有符号同时被替换。例如，公理为 A、规则为 A → AB 和 B → A 时，前几代依次是 "
    "A、AB、ABA、ABAAB 和 ABAABABA，它们的长度 1、2、3、5、8 正是斐波那契数列。"))
story.append(P(
    "L-系统本身只产生字符串。Prusinkiewicz（1986）指出，如果把每个符号当作给海龟的一条命令，字符串就能变成植物的图像。"
    "海龟是一种 LOGO 风格的绘图光标（Abelson &amp; diSessa, 1981）：F 表示向前移动并画线，+ 和 − 表示转向，"
    "方括号 [ 和 ] 分别保存和恢复海龟的状态，这样就能长出一根树枝，再回到主干上。这些思想在"
    "《植物的算法之美》（Prusinkiewicz &amp; Lindenmayer, 1990）中有详细讲解，这本书是我的主要参考资料。"))
story.append(P(
    "我的目标按照作业要求设定：从配置文件读取 L-系统参数，显示模型，用热键逐步改变迭代次数，用热键加载至少八个不同的文件"
    "（其中六个是书中图 1.24 的植物），并用热键改变至少三个参数。我还想尝试两个建议的额外功能——3D 和随机 L-系统，"
    "同时让代码保持足够简短，使我能解释其中的每一行。"))

# ---------------------------------------------------------------- features
story.append(Paragraph("功能", h1))
story.append(Paragraph("配置文件", h2))
story.append(P(
    f"每个 L-系统单独保存在 {M('Assets/StreamingAssets/LSystems')} 中的一个文本文件里。我选用了简单的 "
    f"key=value 格式，方便手工阅读和修改。以 # 开头的行是注释，我用它来注明每个 L-系统的出处。规则写成 "
    f"{M('symbol:successor')}，随机规则则写成 {M('symbol:probability:successor')}。可选的 {M('ratio')} "
    f"键设定每根树枝比它的父枝短多少。代码清单 1 是植物 D 的文件，表 1 列出了全部十个文件。"))
story.append(KeepTogether([Preformatted(
    "# Prusinkiewicz & Lindenmayer (1990), Fig. 1.24d (node rewriting)\n"
    "name=Plant D\n"
    "axiom=X\n"
    "rule=X:F[+X]F[-X]+X\n"
    "rule=F:FF\n"
    "iterations=7\n"
    "angle=20", code),
    Paragraph("<font name='Hei'>代码清单 1</font>  配置文件 04_PlantD.txt。", caption)]))

rows = [["按键", "文件", "公理与规则", "n", "δ"],
        ["1", "植物 A", "F<br/>F → F[+F]F[-F]F", "5", "25.7°"],
        ["2", "植物 B", "F<br/>F → F[+F]F[-F][F]", "5", "20°"],
        ["3", "植物 C", "F<br/>F → FF-[-F+F+F]+[+F-F-F]", "4", "22.5°"],
        ["4", "植物 D", "X<br/>X → F[+X]F[-X]+X, F → FF", "7", "20°"],
        ["5", "植物 E", "X<br/>X → F[+X][-X]FX, F → FF", "7", "25.7°"],
        ["6", "植物 F", "X<br/>X → F-[[X]+X]+F[+FX]-X, F → FF", "5", "22.5°"],
        ["7", "随机植物", "F<br/>F →(0.33) F[+F]F[-F]F<br/>F →(0.33) F[+F]F<br/>F →(0.34) F[-F]F", "5", "25.7°"],
        ["8", "3D 灌木", "A<br/>A → [&amp;FL!A]/////[&amp;FL!A]///////[&amp;FL!A]<br/>F → S/////F, S → FL", "7", "22.5°"],
        ["9", "3D 树", "FFA<br/>A → F[&amp;&amp;FA]/////[&amp;&amp;FA]///////[&amp;&amp;FA]FA", "5", "20°"],
        ["0", "龙形曲线", "FX<br/>X → X+YF+, Y → -FX-Y", "10", "90°"]]
story.append(table_caption("十个配置文件"))
story.append(table(rows, [1.1 * cm, 3.4 * cm, 9.2 * cm, 0.9 * cm, 1.4 * cm], mono_cols=(2,)))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "<i>注：</i>文件 1–6 是 Prusinkiewicz 与 Lindenmayer（1990）的图 1.24 a–f。文件 7 是书中的随机示例（1.7 节），"
    "文件 8 使用书中图 1.25 的产生式 p1–p3（不含叶子），文件 9 是我在书中图 2.8 分枝方式基础上做的变体（长度比例 0.65），"
    "文件 10 是 Bourke（1991）中的 Heighway 龙形曲线。", ParagraphStyle("note", parent=cell, spaceAfter=10)))

story.append(Paragraph("热键", h2))
story.append(P(
    "热键只使用方向键和数字键（表 2），这样字母键可以留给菜单里的规则输入。上下方向键改变迭代次数，用户可以一步一步地看植物生长。"
    "热键可以改变四个参数：迭代次数、分枝角度、分枝长度比例和随机种子。光标在输入框中时热键会被关闭，所以输入数字不会误加载文件。"
    "每次修改后，整个模型都从公理重新生成。为了防止程序卡死，迭代次数上限为 12，字符串上限为一百万个符号；"
    "如果某次修改会超过上限，程序会退回一次迭代并显示提示信息。"))
keys = [["按键", "作用", "按键", "作用"],
        ["1–9, 0", "加载文件 1–10（小键盘同样可用）", "↑ / ↓", "迭代次数 +1 / −1"],
        ["← / →", "角度 −1° / +1°", "Shift + ↑ / ↓", "随机种子 +1 / −1"],
        ["Shift + ← / →", "长度比例 −0.05 / +0.05", "右键拖动", "旋转相机"],
        ["滚轮", "缩放", "", ""]]
story.append(table_caption("热键"))
story.append(table(keys, [2.6 * cm, 5.4 * cm, 2.6 * cm, 5.4 * cm]))
story.append(Spacer(1, 8))
story.append(P(
    "屏幕左侧的菜单用 Unity 的即时模式 GUI（OnGUI 和 GUILayout）制作，显示当前文件，并提供同样的鼠标操作："
    "上一个/下一个文件按钮，迭代次数、角度和长度比例滑条，生成新随机种子的按钮，以及自动旋转、截图和隐藏菜单的按钮。"
    "菜单还显示符号数、线段数和热键列表。"))
story.append(P(
    "<b>规则编辑器。</b>菜单中有一个公理输入框和一个较大的规则输入框，规则每行一条，格式与文件相同"
    f"（{M('F:F[+F]F')} 或 {M('F:0.5:F[+F]')}）。加载文件时，它的公理和规则会被复制到输入框中。"
    "点击 Apply rules 时，程序用读取文件的同一个函数读取输入框并重新生成模型，因此不必退出 Play 模式就能尝试新的 L-系统。"
    "如果某一行无法识别，模型保持不变，菜单会提示是哪一行出错。Reload file 恢复为文件中的规则。"))
if os.path.exists(os.path.join(FIG, "ui.png")):
    story.append(figure(["ui.png"], "程序运行界面，左侧为菜单和规则编辑器。"))

story.append(Paragraph("额外功能", h2))
story.append(P(
    "<b>3D 海龟。</b>海龟用四元数而不是单一角度来保存朝向。除了 + 和 −，它还能理解 &amp; 和 ^（向下/向上俯仰）、"
    "\\ 和 /（向左/向右滚转）以及 |（掉头），这些是书中 1.5 节介绍的 3D 命令。由于 + 和 − 绕 Z 轴旋转，"
    "2D 植物保持在 XY 平面内，并且与 3D 植物由完全相同的代码绘制。"))
story.append(P(
    "<b>随机规则。</b>当一个符号有多条规则时，每次重写该符号都会随机选择其中一条，被选中的机会与其概率成正比"
    "（Prusinkiewicz &amp; Lindenmayer, 1990, 1.7 节）。随机数来自用文件种子创建的生成器，所以同一个种子总是得到同一株植物，"
    f"改变种子（Shift + ↑ / ↓ 或 New seed 按钮）则得到同一类型的另一株植物（图 {FN['seed']}）。"))
story.append(P(
    "<b>分枝长度比例与颜色。</b>每个 [ 都把步长乘以这个比例，因此侧枝比它所长出的枝干短"
    f"（图 {FN['angle']}）。每条线段还记录自己处在第几层括号中，颜色从树干的棕色渐变到枝梢的绿色。"))
story.append(P(
    "<b>3D 树枝与叶子。</b>菜单中的一个勾选框可以把线条切换为实体模型。每条线段变成一根六棱柱形的管子。"
    "构造方法是：先用叉积求出两个与线段垂直的方向，再用角度的 cos 和 sin 在线段起点和终点周围各放六个点，"
    "就像在圆上取点一样；相邻的点用两个三角形连接。半径为 r = r<sub>0</sub> · 0.7<sup><i>d</i></sup>，"
    "其中 <i>d</i> 是括号深度，所以每一级树枝都比它的上一级细。每个 ]（树枝末端）和每个 L 处会添加一片叶子。"
    "叶子是由两个三角形组成的菱形，它的顶点先在海龟自身的坐标系中写出，再用海龟的四元数旋转，因此叶子与所在树枝朝向一致。"
    "树干半径和叶子长度都取植物尺寸的一个百分比，所以同一组设置对小模型和大模型都适用。"
    "树枝和叶子是同一个网格的两个子网格，分别使用受场景光照影响的棕色和绿色材质"
    f"（图 {FN['solid']}）。"))
story.append(P(
    "<b>轨道相机。</b>每次重新生成后，相机都会移动到能完整显示模型的位置。按住鼠标右键可绕模型旋转相机，滚轮用于缩放。"))
story.append(P(
    "<b>图标按钮。</b>菜单旁边有一列三个带图标的按钮：一个退出程序（在编辑器中则停止 Play 模式），一个让背景在浅灰、深色和天蓝之间切换，"
    "一个锁定相机旋转，这样在调整参数时视角不会被意外转动；挂锁图标显示当前是否锁定。鼠标悬停在按钮上时会显示按钮名称。"
    "这些按钮写在一个单独的简短脚本 MyButtons 中，图标从 Resources 文件夹加载。"))

# ---------------------------------------------------------------- data classes
story.append(Paragraph("数据类与数据结构", h1))
story.append(P(
    "程序共有五个脚本。MyLSystem 是放在场景中的 MonoBehaviour，程序启动时它会自动添加 MyCamera 和 MyButtons；"
    "另外两个脚本负责 L-系统的逻辑，不依赖于场景。"))
classes = [["脚本", "内容", "用途"],
           ["MyRewriter.cs", "class Rule, static class MyRewriter", "保存一条规则；把公理重写 n 次"],
           ["MyTurtle.cs", "struct Segment, static class MyTurtle", "读取字符串，返回线段列表"],
           ["MyLSystem.cs", "class MyLSystem : MonoBehaviour", "加载文件、热键、菜单、生成网格"],
           ["MyCamera.cs", "class MyCamera : MonoBehaviour", "让模型充满画面、绕其旋转、旋转锁定"],
           ["MyButtons.cs", "class MyButtons : MonoBehaviour", "退出、背景颜色和锁定按钮"]]
story.append(table_caption("五个脚本"))
story.append(table(classes, [3.2 * cm, 6.0 * cm, 6.7 * cm], mono_cols=(0, 1)))
story.append(Spacer(1, 8))
story.append(Paragraph("规则（Rule）", h2))
story.append(P(
    f"一条 {M('Rule')} 有三个字段：左边的符号（{M('char')}）、右边的后继字符串，以及一个概率。当前 L-系统的规则保存在一个 "
    f"{M('List&lt;Rule&gt;')} 中。我用列表而不是字典，因为在随机 L-系统中一个符号可以有多条规则。"))
story.append(Paragraph("海龟状态与栈", h2))
story.append(P(
    f"海龟的状态是一个小结构体，包含位置（{M('Vector3')}）、朝向（{M('Quaternion')}）、当前步长和括号深度。"
    f"括号使用 {M('Stack&lt;State&gt;')}：[ 压入状态的一份副本，] 将其弹出。栈是合适的结构，因为树枝是嵌套的："
    f"最后打开的树枝总是最先关闭。由于状态是结构体，栈中保存的是副本，所以在树枝内部转向不会改变主干保存的状态。"))
story.append(Paragraph("线段与网格", h2))
story.append(P(
    f"每个 F 产生一个 {M('Segment')}，包含起点、终点和深度。之后 MyLSystem 把所有线段放进一个用 "
    f"{M('MeshTopology.Lines')} 绘制的 Unity {M('Mesh')} 中：每条线段两个顶点、两个索引，外加一个顶点颜色。"
    f"使用单个网格意味着即使是有 4,096 条线的植物 C，也只需一次绘制调用。网格使用 32 位索引，"
    f"这样较大的模型也不会超过 16 位索引 65,535 个顶点的上限。"))

# ---------------------------------------------------------------- main structure
story.append(Paragraph("主要结构", h1))
fig_no[0] += 1
story.append(KeepTogether([pipeline(), Paragraph(
    f"<font name='Hei'>图 {fig_no[0]}</font>  加载文件或修改参数时的处理流程。", caption)]))
steps = [
    f"<b>启动。</b>{M('Init()')} 创建网格和材质，添加相机脚本，并按字母顺序列出文本文件，然后加载第一个文件。",
    f"<b>加载。</b>{M('LoadFile()')} 逐行读取文件，在第一个 = 号处把每行分开，把值存入对应的字段。"
    f"数字用固定区域设置（invariant culture）解析，所以在使用小数逗号的语言环境下 25.7 也能被正确读取。",
    f"<b>重写。</b>{M('MyRewriter.Generate()')} 重复重写 n 次。每次迭代读取当前字符串，把结果写入一个新的 "
    f"{M('StringBuilder')}，因此所有符号是并行替换的，新产生的符号要到下一次迭代才会被重写。",
    f"<b>海龟。</b>{M('MyTurtle.Draw()')} 把字符串遍历一遍。F 让海龟移动 {M('rotation * Vector3.up * length')} "
    f"并记录一条线段；旋转符号把四元数乘以 {M('Quaternion.Euler(...)')}；方括号对栈进行压入和弹出。",
    f"<b>网格与相机。</b>{M('BuildMesh()')} 填充网格，{M('MyCamera.Frame()')} 把相机放在距离 d = r / sin(θ/2) 处，"
    f"其中 r 是模型包围球的半径，θ 是相机的视野角。在这个距离上整个球体正好能装进画面。",
    f"<b>热键与菜单。</b>{M('Update()')} 每帧检查按键，{M('OnGUI()')} 绘制菜单。"
    f"如果按键、滑条或规则编辑器改变了什么，它们就调用 {M('Rebuild()')}，重新执行第 3–5 步。",
]
for s in steps:
    story.append(P(s, ParagraphStyle("st", parent=body, firstLineIndent=0, leftIndent=0.5 * cm, spaceAfter=3)))
story.append(P(
    f"有一个细节必须处理正确：四元数乘法的顺序。写成 {M('rotation = rotation * turn')} 时，旋转是绕海龟自身的坐标轴进行的，"
    "这正是 L-系统符号的含义（例如 &amp; 让树枝相对于海龟当前的朝向向下俯仰）。"
    f"如果写成 {M('turn * rotation')}，旋转就会绕世界坐标轴进行，3D 模型就会出错。"))

# ---------------------------------------------------------------- results
story.append(Paragraph("结果", h1))
story.append(P(
    f"本节所有图片都是程序根据配置文件渲染的。图 {FN['plants']} 是作业要求的六种植物，它们的形状与书中图 1.24 a–f 一致。"))
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
    f"<font name='Hei'>图 {fig_no[0]}</font>  文件 1–6：程序绘制的 Prusinkiewicz 与 Lindenmayer（1990）图 1.24 a–f 中的六种植物。",
    caption)]))

story.append(P(
    f"图 {FN['iter']} 是植物 A 经过 1 到 5 次迭代的结果。每个 F 变成五个 F，所以线段数为 5<super>n</super>：" +
    "、".join(fmt(ST[f"iterA_{n}"]["segments"]) for n in range(1, 6)) +
    "。整个字符串的长度也以同样方式增长：" +
    "、".join(fmt(ST[f"iterA_{n}"]["symbols"]) for n in range(1, 6)) +
    " 个符号，即 (5<super>n+1</super> − 3) / 2。"))
story.append(figure([f"iterA_{n}.png" for n in range(1, 6)], "植物 A 经过 1 到 5 次迭代（上方向键）。",
                    labels=[f"n = {n}" for n in range(1, 6)]))
story.append(P(
    f"图 {FN['angle']} 显示角度和长度比例热键的效果。文法不变，但较小的角度得到窄的植物，较大的角度得到宽的植物；"
    "较小的比例让侧枝变短，使植物更像一棵主干清晰的树。"))
story.append(figure(["angleE_15.png", "angleE_25.7.png", "angleE_40.png", "ratioD_1.0.png", "ratioD_0.8.png",
                     "ratioD_0.6.png"],
                    "左：植物 E，角度为 15°、25.7° 和 40°（左右方向键）。右：植物 D，长度比例为 1.0、0.8 和 0.6（Shift + ← / →）。",
                    labels=["15°", "25.7°", "40°", "1.0", "0.8", "0.6"]))
story.append(P(
    f"图 {FN['seed']} 是随机植物的四个种子。它们使用相同的三条规则，但由于不同位置选中了不同的规则，"
    "每株植物都有自己的形状和大小（线段数在 " +
    f"{min(int(ST[f'seed_{s}']['segments']) for s in (1, 2, 3, 4))} 到 "
    f"{max(int(ST[f'seed_{s}']['segments']) for s in (1, 2, 3, 4))} 之间）。"))
story.append(figure([f"seed_{s}.png" for s in (1, 2, 3, 4)], "文件 7，随机植物，种子为 1 到 4（Shift + ↑）。",
                    labels=[f"种子 {s}" for s in (1, 2, 3, 4)]))
story.append(P(
    f"图 {FN['tree']} 和图 {FN['bush']} 是 3D 模型。3D 树有一根主干，每个节点长出三根侧枝，"
    "这些侧枝被滚转符号绕主干转开，所以从上方看，树枝向各个方向伸展。"))
story.append(figure(["iter3d_2.png", "iter3d_4.png", "09.png", "tree3d_top.png"],
                    "文件 9，3D 树，经过 2、4 和 5 次迭代，以及俯视图。",
                    labels=["n = 2", "n = 4", "n = 5", "俯视图"]))
story.append(figure(["08.png", "10.png"], "文件 8，3D 灌木；文件 10，龙形曲线。",
                    labels=["3D 灌木", "龙形曲线"], max_h=7 * cm))

story.append(figure(["solid_A.png", "solid_E.png", "solid_tree.png", "solid_bush.png"],
                    "同样的 L-系统用 3D 树枝和叶子绘制：植物 A、植物 E、3D 树和 3D 灌木。",
                    labels=["植物 A", "植物 E", "3D 树", "3D 灌木"], max_h=6.5 * cm))

sizes = [["文件", "n", "符号数", "线段数"]]
for k in ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]:
    sizes.append([NAMES[k], ST[k]["n"], fmt(ST[k]["symbols"]), fmt(ST[k]["segments"])])
story.append(P(
    "表 4 列出了每个模型在默认迭代次数下的规模。最大的 3D 灌木约有 47,000 个符号和 3,900 条线段，所有模型都能在没有明显停顿的情况下重新生成。"))
story.append(table_caption("各模型的规模"))
story.append(table(sizes, [5.5 * cm, 1.5 * cm, 4.0 * cm, 4.0 * cm]))
story.append(Spacer(1, 6))

# ---------------------------------------------------------------- conclusion
story.append(Paragraph("结论", h1))
story.append(P(
    "程序完成了作业要求：它读取十个配置文件，每个文件有自己的加载键；正确绘制了要求的六种植物；可以用方向键逐步改变迭代次数；"
    "并且可以用热键改变四个参数。我还加入了带规则编辑器的菜单、3D 海龟、带叶子的 3D 树枝、随机规则、分枝长度比例、"
    "按深度着色和轨道相机。把重写、海龟和绘制分在不同脚本中，让程序更容易编写和测试，因为我可以先在控制台检查字符串，再去做绘制部分。"))
story.append(P(
    "程序也有一些明显的局限。3D 树枝是一根根独立的管子，所以两根树枝以较大角度相接处能看到小缝隙，叶子也是平的，形状都一样。"
    "这些 L-系统是上下文无关且非参数化的，所以无法表达在植物中传递信号的效果（上下文相关 L-系统，书中 1.8 节）"
    "或长度取决于年龄的树枝（参数化 L-系统，1.10 节）。向性（tropism）能让树枝朝重力或光线方向弯曲（2.2 节），"
    "也会让 3D 树更逼真。TreeSketch（Longay et al., 2012）这样的交互式工具展示了这些思想能走多远。"))
story.append(P(f"程序的视频演示：{VIDEO_URL}。"))
story.append(Spacer(1, 8))
wc_pos = len(story)
story.append(Paragraph("", body_ni))

# ---------------------------------------------------------------- references
story.append(PageBreak())
story.append(Paragraph("参考文献", h1))
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

story[wc_pos] = Paragraph(f"<i>字数（摘要至结论，不含表格、代码清单、图注和参考文献；汉字与英文单词合计）：{chars[0]:,}</i>",
                          body_ni)
doc.build(story)
print("chars:", chars[0])
