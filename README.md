# Friday 20 November 2026 — one front page

One image that sums up Friday 20 November 2026's world news:
**39 stories across 6 continents**, as a newspaper front page with a
dotted world map, the day in numbers, three lead stories and a numbered
grid of every story. Each story is real, first reported on 20 November
2026, and carries its source in `app/stories.json`.

## Layout

- `main.ts` — the entrypoint (Node 22, stdlib only). It writes the
  pre-rendered `entry.png` beside it to `$MAKEFUN_OUTPUT_DIR/entry.png`.
- `entry.png` — the front page (1024×1024, PNG).
- `app/render.py` — the renderer (Python + Pillow). It draws the page
  from `app/stories.json`. Rebuild with `python3 app/render.py entry.png`.
- `app/stories.json` — the 39 stories (headline, source, region) and the
  day-in-numbers figures.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

The program writes `out/entry.png` and exits 0. It is deterministic:
run it twice and the bytes are identical.

## Licence

MIT — see `LICENSE`.
