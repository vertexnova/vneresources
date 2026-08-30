#!/usr/bin/env python3
# ==============================================================================
# Copyright (c) 2026 Ajeet Singh Yadav. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# Author:    Ajeet Singh Yadav
# Created:   August 2026
#
# Autodoc:   yes
# ==============================================================================
"""Extract articulated link assets from Franka Robotics' official FR3 USD.

The published stage stores link visuals as internal USD references. Assimp's
tinyusdz importer does not compose those references, so this tool asks
``usdcat --flatten`` to make one self-contained crate per articulated link.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path

OFFICIAL_FR3_URL = "https://franka.de/hubfs/FR3.usd?hsLang=en"
OFFICIAL_FR3_SHA256 = "11a5901d9d70dcae48ae6338984a8c90d9e2b1a5409f2377785cc356b5551719"
DEFAULT_OUTPUT = Path(__file__).resolve().parent


def download_official_usd(path: Path) -> None:
    print(f"Downloading {OFFICIAL_FR3_URL}")
    urllib.request.urlretrieve(OFFICIAL_FR3_URL, path)


def verify_source(path: Path) -> None:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != OFFICIAL_FR3_SHA256:
        raise RuntimeError(
            f"Unexpected FR3 USD SHA-256: {digest}\n"
            f"Expected: {OFFICIAL_FR3_SHA256}"
        )


def link_wrapper(link: int, source: Path) -> str:
    source_asset = source.resolve().as_posix()
    children = f'''
    def Xform "visual" (
        prepend references = @{source_asset}@</fr3/fr3v2_link{link}/visuals>
    )
    {{
    }}
'''

    return f'''#usda 1.0
(
    defaultPrim = "fr3_link{link}"
    doc = "Extracted from Franka Robotics' official FR3 USD."
    metersPerUnit = 1
    upAxis = "Z"
)

def Xform "fr3_link{link}"
{{{children}}}
'''


def extract_links(source: Path, output: Path, usdcat: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="fr3-usd-") as temp_dir:
        temp = Path(temp_dir)
        for link in range(8):
            wrapper = temp / f"fr3_link{link}.usda"
            wrapper.write_text(link_wrapper(link, source), encoding="utf-8")
            destination = output / f"fr3_link{link}.usd"
            subprocess.run(
                [usdcat, str(wrapper), "--flatten", "-o", str(destination)],
                check=True,
            )
            print(f"Wrote {destination} ({destination.stat().st_size / 1024:.0f} KiB)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Previously downloaded official FR3.usd")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    usdcat = shutil.which("usdcat")
    if usdcat is None:
        raise RuntimeError("usdcat is required to flatten the official USD references")

    if args.source is not None:
        source = args.source
        verify_source(source)
        extract_links(source, args.out, usdcat)
        return 0

    with tempfile.TemporaryDirectory(prefix="fr3-source-") as temp_dir:
        source = Path(temp_dir) / "FR3.usd"
        download_official_usd(source)
        verify_source(source)
        extract_links(source, args.out, usdcat)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
