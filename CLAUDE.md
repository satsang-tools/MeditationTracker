# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-screen meditation/sitting timer ("Sitting") shipped as an installable, offline PWA.
There is **no build step, no framework, no dependencies, and no tests** — the entire app is
inline HTML/CSS/JS in `index.html`. All user data is local to the device.

## Commands

- **Run locally** (a service worker needs `http`/`localhost`, not `file://`):
  ```sh
  python -m http.server 8000   # or: npx serve .
  ```
  then open the printed `http://localhost:…` URL.
- **Regenerate app icons** (after editing `icon.svg`): `python make_icons.py` (needs `pip install Pillow`).
  `icon.svg` is the master; everything in `icons/` is generated from it.
- **Regenerate the review mock**: `python3 preview/render.py` writes `preview/preview.png`. This is a
  Pillow render of the whole screen used to eyeball changes without a browser (the environment can't
  install one). `preview/` is gitignored and is **not** part of the app — keep it in sync manually when
  the chart/layout changes.
- **Deploy**: static site served by GitHub Pages ("Deploy from a branch", root) at
  `https://satsang-tools.github.io/MeditationTracker/`. A pushed change to the served branch redeploys
  automatically.

## Critical convention: bump the service-worker cache

`sw.js` is cache-first over a fixed app shell. After **any** change to `index.html`/`manifest`/icons,
increment the `CACHE` string in `sw.js` (e.g. `sitting-v8` → `sitting-v9`), or installed clients keep
serving the old shell. This is the single most common way to ship a "silent no-op".

## Architecture (all in `index.html`)

One IIFE holds the app; a tiny second `<script>` registers the service worker.

- **Data model** — `localStorage["mt_state"] = { sessions:[{s,e}], active:startMs|null }`.
  - **Time is timestamp-based, never counter-based.** `begin()` stores `Date.now()` as `active` and
    persists immediately; durations are always derived from wall-clock timestamps, so a long sit stays
    correct across screen-off, backgrounding, or PWA eviction. The `pace()` interval only triggers
    re-renders — it never accumulates elapsed time.
  - Recorded times are rounded to the nearest minute (`roundMin`). `pruneOld(now)` drops sessions that
    ended more than `NWIN` (5) days ago — the longest window the chart uses — and runs on load, on
    `finish()`, and on `resume()`.

- **Stats → chart** — `computeWindows(now)` returns 5 trailing moving averages (avg hours/day over the
  last N=1..5 days), `vals[0]`=today … `vals[4]`=5d, including any in-progress sit. `drawVals()` plots
  them left→right (5d→today) as a smooth Catmull-Rom curve (`smoothPath`) with an area fill and circle
  nodes (today's node glows).

- **Adaptive vertical axis** — `computeTop(vals) = max(1, floor(maxAvg)+1)` hours, so the scale grows
  one hour at a time and always keeps headroom. `buildGrid()` redraws gridlines, hour labels, day
  labels, and the 10-minute right-edge ticks (drawn at every 10 min for every hour, always present).

- **Responsive layout** — CSS splits the screen: `.chart-wrap` is the top **two-thirds**, `.middle`
  (the round control) is the bottom **third**. The SVG carries `preserveAspectRatio="none"`; `layout()`
  measures the SVG's real pixel box and sets the `viewBox` 1:1 to those pixels, so strokes/text never
  distort at any aspect ratio. `layout()` + `buildGrid()` + `drawVals()` re-run on resize,
  orientationchange, and `resume()` (`visibilitychange`/`pageshow`/`focus`).

- **Render loop** — `render(animate)` recomputes the windows, updates `TOP` (rebuilding the grid if it
  changed), then eases `disp` toward the target (easeOutCubic) and calls `drawVals`. `reflectState()`
  flips the control label between **Begin**/**Finish**.

## Visual language (CSS custom properties in `:root`)

Cool near-black background (`--bg #0B0D11`); electric-blue glow (`--blue #2E86FF`) for the curve and the
control ring; cream-white (`--ink #EFE6D4`) for the button label **and** all chart numbers/labels; warm
`--gold-dim` only for the 10-minute ticks. Keep `manifest.webmanifest` `theme_color`/`background_color`
and the `<meta name="theme-color">` in sync with `--bg`.
