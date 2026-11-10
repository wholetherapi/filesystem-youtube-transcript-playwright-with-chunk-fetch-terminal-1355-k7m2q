#!/usr/bin/env python3
"""Minimal site build: validates the chapter manifest against the published
transcript rows. Files under templates/ are legacy prototypes and are not read
by this build."""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    manifest = json.load(open(os.path.join(ROOT, "content", "chapters.json"), encoding="utf-8"))
    transcripts = os.path.join(ROOT, "content", "transcripts")
    rows = 0
    if os.path.isdir(transcripts):
        for name in sorted(os.listdir(transcripts)):
            if name.endswith(".jsonl"):
                rows += sum(1 for line in open(os.path.join(transcripts, name), encoding="utf-8") if line.strip())
    print("episode=%s chapters=%d cue_rows=%d" % (manifest.get("episode_id"), len(manifest.get("chapters", [])), rows))
    print("templates/ is reference-only and is not consumed by this build")
    return 0


if __name__ == "__main__":
    sys.exit(main())
