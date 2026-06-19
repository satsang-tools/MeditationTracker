# Sitting

A quiet, single-screen timer for sitting practice. Press **Begin** to start a sit and
**Finish** to end it; the curve shows your average hours/day over the trailing 1–5 days.
The vertical scale adapts to your practice — it begins at one hour (with ten-minute ticks on
the right) and steps up an hour at a time whenever any of the five averages reaches the top,
so a few-minutes-a-day sitter and a several-hours-a-day sitter both get a readable curve.
Built as an installable PWA — it runs full-screen on your phone and works offline, with all
data kept locally on the device.

## How time is kept (accurate across sleep / backgrounding)

A sit is **timestamp-based, never counter-based**. Beginning a sit records an absolute start
time (`Date.now()`) and writes it to `localStorage` immediately; the elapsed duration is
always derived from wall-clock timestamps. The on-screen interval only triggers re-draws — it
never accumulates time. So a multi-hour sit stays exact even if the screen turns off, the
phone sleeps, the app is backgrounded, or the PWA is evicted from memory: reopening restores
the start time and the recorded duration is still correct. (The app deliberately does **not**
hold a Wake Lock — the screen is free to sleep.)

## Data

All history lives in the browser's `localStorage` under the key `mt_state`
(`{ sessions: [{s,e}], active: startMs|null }`). It is **per-device** — there is no account
or cross-device sync. Clearing the browser/app data clears the history.

## Run locally

A service worker needs `http(s)` or `localhost` — it will not register from a `file://` path,
so open it through a local server:

```sh
# any one of these, from this folder:
npx serve .
# or
python -m http.server 8000
```

Then visit the printed `http://localhost:…` URL.

## Deploy

It's a static site (no build step). Any static host works:

- **Netlify** — drag this folder onto https://app.netlify.com/drop for an instant HTTPS URL.
- **GitHub Pages** — push this repo to GitHub, then enable Pages on the default branch (root).
- **Vercel / Cloudflare Pages** — point them at the repo; no build command, output is root.

## Install on your phone

1. Open the deployed HTTPS URL in mobile Chrome (Android) or Safari (iOS).
2. Use **Add to Home Screen** (Share menu on iOS; ⋮ menu on Android).
3. Launch from the home-screen icon — it opens full-screen and runs offline.

## Updating

To ship changes after the service worker is live, bump the `CACHE` version string in
[`sw.js`](sw.js) (e.g. `sitting-v1` → `sitting-v2`) so clients fetch the new shell.

## Files

- `index.html` — the whole app (inline CSS/JS).
- `manifest.webmanifest` — PWA metadata.
- `sw.js` — offline cache (app shell, cache-first).
- `icon.svg` — master icon; `icons/*.png` are rasterized from it.
- `make_icons.py` — regenerates the PNG icons (`pip install Pillow`, then `python make_icons.py`).
