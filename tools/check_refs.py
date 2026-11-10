#!/usr/bin/env python3
"""Release-gate reference checker for the studio content repository.

Resolves cue anchors used by the chapter manifest and collects every brace
reference key found in the repository content. The release gate fails while any
finding remains.
"""

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
TEMPLATES = os.path.join(ROOT, "templates")


def load_chapters():
    path = os.path.join(CONTENT, "chapters.json")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_cues():
    cues = {}
    starts = {}
    for path in sorted(glob.glob(os.path.join(CONTENT, "transcripts", "*.jsonl"))):
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                cue_id = row.get("id")
                start = row.get("start")
                if cue_id is not None:
                    cues[str(cue_id)] = row
                if isinstance(start, (int, float)):
                    starts[int(start)] = str(cue_id)
    return cues, starts


def hms_to_seconds(text):
    parts = [int(p) for p in str(text).strip().split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def main():
    chapters = load_chapters().get("chapters", [])
    cues, starts = load_cues()
    findings = []

    if not cues:
        findings.append("content/transcripts/*.jsonl: no published transcript found")

    for chapter in chapters:
        cid = chapter.get("chapter_id")
        anchor = str(chapter.get("anchor"))
        start = hms_to_seconds(chapter.get("start", "0:00:00"))
        expected = starts.get(start)
        if anchor not in cues:
            findings.append(
                "%s: chapter %s anchor '%s' is not defined in any transcript"
                % ("content/chapters.json", cid, anchor)
            )
        elif expected is not None and anchor != expected:
            findings.append(
                "%s: chapter %s anchor '%s' does not match the cue starting at %s ('%s')"
                % ("content/chapters.json", cid, anchor, chapter.get("start"), expected)
            )
        if expected is None:
            findings.append(
                "%s: chapter %s start '%s' has no cue at that time"
                % ("content/chapters.json", cid, chapter.get("start"))
            )

    key_pattern = re.compile(r"\{\{\s*\.([A-Za-z0-9_]+)\s*\}\}")
    for path in sorted(glob.glob(os.path.join(TEMPLATES, "*.tmpl"))):
        rel = os.path.relpath(path, ROOT)
        with open(path, "r", encoding="utf-8") as fh:
            body = fh.read()
        for key in sorted(set(key_pattern.findall(body))):
            findings.append("%s: reference key '%s' is not defined" % (rel, key))

    print("Reference check: content/chapters.json + templates/")
    print("=== UNRESOLVED REFERENCE KEYS (%d) ===" % len(findings))
    for finding in findings:
        print("- " + finding)
    print("=== SUMMARY ===")
    print("%d unresolved reference keys" % len(findings))
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
