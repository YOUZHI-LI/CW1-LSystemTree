"""Builds the English and the Chinese report together, so the two PDFs always match.

Usage (in the Report folder):  python build_all.py

The cover details and the video link are set once, at the top of build_report.py;
the Chinese version reads them from there. When you change a paragraph in one
script, change the same paragraph in the other (they follow the same order).
"""
import os
import subprocess
import sys

here = os.path.dirname(os.path.abspath(__file__))
jobs = [("build_report.py", "YouzhiLi-L-system-2026.pdf"),
        ("build_report_zh.py", "YouzhiLi-L-system-2026-CN.pdf")]
for script, pdf in jobs:
    print(f"{script} -> {pdf}")
    subprocess.run([sys.executable, script, "figures", pdf], cwd=here, check=True)
