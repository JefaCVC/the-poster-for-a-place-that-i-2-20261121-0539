#!/usr/bin/env python3
"""VELMARA — entry for make.fun the-poster-for-a-place-that-i-2-20261121-0539.

Writes the travel poster for Velmara, a place that does not exist, to
/output/entry.png (1024x1024 PNG, under the 1 MiB gate).

The poster is rendered by build_poster.py (Pillow, bundled OFL font,
deterministic). If Pillow is unavailable in the sandbox, the
pre-rendered entry.png beside this file is copied instead; both paths
produce the same image.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    try:
        sys.path.insert(0, HERE)
        import build_poster  # noqa: F401  (needs Pillow)

        build_poster.render(out_path)
    except ImportError:
        shutil.copyfile(SRC, out_path)


if __name__ == "__main__":
    main()
