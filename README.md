# robodraw

Minimal generative art starter for a CNC-style drawing robot.

## Repository layout

```text
.
├── docs/                  Notes about software and plotting workflow
├── output/                Generated SVG artifacts, not committed
│   ├── custom/
│   └── upstream/
├── scripts/               Utility scripts and generators
├── sketches/
│   ├── custom/            Original sketches for this repo
│   └── upstream/          Imported third-party example sketches
└── README.md
```

## What this does

- Generates plotter-friendly SVG line art with no external Python dependencies
- Keeps output in physical units (`mm`) so it is easier to feed into a pen plotter workflow
- Produces layered paths you can later optimize with tools such as `vpype`

## Quick start

Run:

```bash
python3 scripts/generate_art.py
```

This writes a sample drawing to `output/custom/flow_fields.svg`.

## Options

```bash
python3 scripts/generate_art.py --help
```

Example:

```bash
python3 scripts/generate_art.py \
  --width-mm 210 \
  --height-mm 297 \
  --seed 7 \
  --columns 120 \
  --rows 170 \
  --steps 28 \
  --stroke-width-mm 0.22 \
  --output output/custom/a4_flow.svg
```

## Next steps for a real robot

Suggested software path:

1. Generate SVG here
2. Optimize paths with `vpype`
3. Convert SVG to G-code if needed
4. Send to the machine with `UGS` or `cncjs`

## Files

- `scripts/generate_art.py`: dependency-free SVG generator
- `sketches/custom/flow_field/sketch_flow_field.py`: custom `vsketch` flow field
- `sketches/upstream/vsketch/`: imported upstream examples
- `output/`: generated local artifacts
- `docs/`: notes and references

## vsketch setup

`vsketch` requires Python 3.13 on this machine because the system `python3` is 3.14 and current `vsketch` releases do not support it yet.

Repo-local environment:

- `.venv-vsketch`
- `.uv-cache`
- `.uv-python`

Activate it with:

```bash
source /Users/vlad/Dev/robodraw/.venv-vsketch/bin/activate
```

To avoid cache warnings in this sandboxed repo, set:

```bash
export MPLCONFIGDIR=/Users/vlad/Dev/robodraw/.mplconfig
export XDG_CACHE_HOME=/Users/vlad/Dev/robodraw/.cache
```

## vsketch usage

Interactive viewer:

```bash
MPLCONFIGDIR=/Users/vlad/Dev/robodraw/.mplconfig \
XDG_CACHE_HOME=/Users/vlad/Dev/robodraw/.cache \
/Users/vlad/Dev/robodraw/.venv-vsketch/bin/vsk run /Users/vlad/Dev/robodraw/sketches/custom/flow_field
```

Export directly to SVG:

```bash
MPLCONFIGDIR=/Users/vlad/Dev/robodraw/.mplconfig \
XDG_CACHE_HOME=/Users/vlad/Dev/robodraw/.cache \
/Users/vlad/Dev/robodraw/.venv-vsketch/bin/vsk save /Users/vlad/Dev/robodraw/sketches/custom/flow_field -n flow_field -d /Users/vlad/Dev/robodraw/output/custom/flow_field
```

Override parameters on export:

```bash
MPLCONFIGDIR=/Users/vlad/Dev/robodraw/.mplconfig \
XDG_CACHE_HOME=/Users/vlad/Dev/robodraw/.cache \
/Users/vlad/Dev/robodraw/.venv-vsketch/bin/vsk save /Users/vlad/Dev/robodraw/sketches/custom/flow_field \
  -n flow_field_dense \
  -d /Users/vlad/Dev/robodraw/output/custom/flow_field \
  -p columns 90 \
  -p rows 120 \
  -p steps 30 \
  -p step_mm 1.4 \
  -p swirl 1.1 \
  -s 7
```

Use `-d` to keep exports centralized under the top-level `output/` directory.

## vsketch example

The first `vsketch` sketch is in `sketches/custom/flow_field/sketch_flow_field.py`.

It demonstrates:

- sketch parameters with `vsketch.Param`
- millimeter-based page sizing
- deterministic generation with a seed
- `vpype` cleanup in `finalize()` for better plotting

## Upstream vsketch examples

Official example sketches from `abey79/vsketch` have been copied into:

- `sketches/upstream/vsketch/`

These are source examples only. Upstream generated `output/` directories were intentionally not copied.

Useful examples to start with:

- `sketches/upstream/vsketch/random_lines/sketch_random_lines.py`
- `sketches/upstream/vsketch/random_flower/sketch_random_flower.py`
- `sketches/upstream/vsketch/schotter/sketch_schotter.py`
- `sketches/upstream/vsketch/prime_circles/sketch_prime_circles.py`
- `sketches/upstream/vsketch/transforms/sketch_transforms.py`
- `sketches/upstream/vsketch/shapely/sketch_shapely.py`

Run one in the viewer:

```bash
vsk run /Users/vlad/Dev/robodraw/sketches/upstream/vsketch/random_lines
```

Export one to SVG:

```bash
vsk save /Users/vlad/Dev/robodraw/sketches/upstream/vsketch/random_lines -n random_lines -d /Users/vlad/Dev/robodraw/output/upstream/random_lines
```

The upstream examples README is copied to:

- `sketches/upstream/vsketch/UPSTREAM_README.md`

## Automatic shell setup

This repo uses `direnv`.

The project environment is defined in `.envrc`, which:

- activates `/Users/vlad/Dev/robodraw/.venv-vsketch`
- sets `MPLCONFIGDIR`
- sets `XDG_CACHE_HOME`

`direnv` has been installed and the standard hook has been added to `~/.zshrc`.

To allow this repo:

```bash
cd /Users/vlad/Dev/robodraw
direnv allow
```

After that:

- entering `/Users/vlad/Dev/robodraw` auto-loads the environment
- leaving the directory unloads it automatically
