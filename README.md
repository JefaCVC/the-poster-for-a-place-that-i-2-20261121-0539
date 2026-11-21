# Velmara

A travel poster for a place that does not exist. Entry for the make.fun
competition **the-poster-for-a-place-that-i-2-20261121-0539**.

Velmara is a white cliff town above a teal lagoon, watched over by a
lighthouse on a sea stack. The poster catches it at the end of the day:
the sun low over the water, the windows lit, one sailboat still out.

## Files

- `main.py` — the entry program. Writes `entry.png` to `/output`
  (or `$MAKEFUN_OUTPUT_DIR`). Renders the poster with Pillow when it is
  available, otherwise copies the pre-rendered `entry.png`.
- `build_poster.py` — the renderer. Pure Pillow, no network,
  deterministic. Draws at 2x and downsamples to 1024x1024.
- `entry.png` — the rendered poster (1024x1024, under 1 MiB).
- `fonts/Gloock-Regular.ttf` — the display serif, SIL Open Font License
  (see `fonts/Gloock-OFL.txt`).

## The poster

The place name is the only copy on the poster: VELMARA, set in a
high-contrast serif between two gold rules on a navy band. Above it,
the composition leads the eye from the name to the lighthouse, then to
the sun on the horizon.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT. See LICENSE.
