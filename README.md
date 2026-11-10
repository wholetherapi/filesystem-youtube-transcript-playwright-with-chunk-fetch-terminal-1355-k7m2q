# Meridian Learning Studio — episode source repository

This repository is the publication source for Meridian Learning Studio's mirror
episodes. Each episode has a static mirror page under `episodes/` and a chapter
manifest under `content/`.

## Layout

- `episodes/e204.html` — public mirror page for episode E204. The page renders
  its transcript panel on demand; cue ids and start times are attached to each
  rendered cue row.
- `content/chapters.json` — chapter manifest consumed by the site build.
  `anchor` must be the cue id whose `start` equals the chapter's `start` time;
  `start` is authoritative.
- `content/transcripts/` — published cue transcripts, one JSON object per line
  with `id`, `start` (whole seconds) and `text`.
- `templates/` — legacy cue renderer prototypes kept for reference while the
  renderer migration is in progress. The current site build and release pipeline
  never load files in this directory.
- `tools/check_refs.py` — reference checker used by the release gate:
  `python tools/check_refs.py`
- `tools/site_build.py` — minimal build used by the release pipeline:
  `python tools/site_build.py`

## Release gate

The gate requires the chapter manifest to resolve against the published
transcript and reports every unresolved reference key it finds across the
checked content. Publish a transcript first, then run the checker.
