#!/usr/bin/env python3

from __future__ import annotations

import argparse
import math
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Point:
    x: float
    y: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate plotter-friendly flow field SVG art."
    )
    parser.add_argument("--width-mm", type=float, default=210.0)
    parser.add_argument("--height-mm", type=float, default=210.0)
    parser.add_argument("--margin-mm", type=float, default=12.0)
    parser.add_argument("--columns", type=int, default=110)
    parser.add_argument("--rows", type=int, default=110)
    parser.add_argument("--steps", type=int, default=24)
    parser.add_argument("--step-mm", type=float, default=1.6)
    parser.add_argument("--stroke-width-mm", type=float, default=0.28)
    parser.add_argument("--stroke-color", default="#111111")
    parser.add_argument("--stroke-opacity", type=float, default=1.0)
    parser.add_argument("--noise-scale", type=float, default=0.028)
    parser.add_argument("--swirl", type=float, default=0.95)
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/custom/flow_fields.svg"),
        help="Output SVG path.",
    )
    args = parser.parse_args()
    validate_args(parser, args)
    return args


def validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.width_mm <= 0 or args.height_mm <= 0:
        parser.error("--width-mm and --height-mm must be positive")
    if args.margin_mm < 0:
        parser.error("--margin-mm must be zero or greater")
    if args.width_mm <= 2 * args.margin_mm or args.height_mm <= 2 * args.margin_mm:
        parser.error("--margin-mm must leave drawable space inside the page")
    if args.columns < 1 or args.rows < 1:
        parser.error("--columns and --rows must be at least 1")
    if args.steps < 1:
        parser.error("--steps must be at least 1")
    if args.step_mm <= 0 or args.stroke_width_mm <= 0 or args.noise_scale <= 0:
        parser.error(
            "--step-mm, --stroke-width-mm, and --noise-scale must be positive"
        )
    if not is_hex_color(args.stroke_color):
        parser.error("--stroke-color must be a hex color like #111111 or #222")
    if not 0 < args.stroke_opacity <= 1:
        parser.error("--stroke-opacity must be greater than 0 and at most 1")


def is_hex_color(value: str) -> bool:
    if len(value) not in {4, 7} or not value.startswith("#"):
        return False
    return all(char in "0123456789abcdefABCDEF" for char in value[1:])


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def field_angle(x: float, y: float, width: float, height: float, scale: float, swirl: float) -> float:
    nx = x * scale
    ny = y * scale
    cx = width / 2.0
    cy = height / 2.0
    dx = x - cx
    dy = y - cy
    radius = math.hypot(dx, dy) + 1e-6

    wave = math.sin(nx * 1.7) + math.cos(ny * 1.3) + math.sin((nx + ny) * 0.9)
    twist = math.atan2(dy, dx) + radius * 0.012 * swirl
    return wave * 1.2 + twist


def build_paths(args: argparse.Namespace) -> list[list[Point]]:
    rng = random.Random(args.seed)
    width = args.width_mm
    height = args.height_mm
    inner_width = width - 2 * args.margin_mm
    inner_height = height - 2 * args.margin_mm
    spacing_x = inner_width / max(args.columns - 1, 1)
    spacing_y = inner_height / max(args.rows - 1, 1)

    paths: list[list[Point]] = []
    for row in range(args.rows):
        for col in range(args.columns):
            jitter_x = (rng.random() - 0.5) * spacing_x * 0.22
            jitter_y = (rng.random() - 0.5) * spacing_y * 0.22
            x = args.margin_mm + col * spacing_x + jitter_x
            y = args.margin_mm + row * spacing_y + jitter_y

            points = [Point(x, y)]
            current_x = x
            current_y = y
            for _ in range(args.steps):
                angle = field_angle(
                    current_x,
                    current_y,
                    args.width_mm,
                    args.height_mm,
                    args.noise_scale,
                    args.swirl,
                )
                current_x += math.cos(angle) * args.step_mm
                current_y += math.sin(angle) * args.step_mm
                current_x = clamp(current_x, args.margin_mm, args.width_mm - args.margin_mm)
                current_y = clamp(current_y, args.margin_mm, args.height_mm - args.margin_mm)
                points.append(Point(current_x, current_y))

            paths.append(points)
    return paths


def svg_path(points: list[Point]) -> str:
    start, *rest = points
    commands = [f"M {start.x:.3f} {start.y:.3f}"]
    commands.extend(f"L {point.x:.3f} {point.y:.3f}" for point in rest)
    return " ".join(commands)


def write_svg(
    paths: list[list[Point]],
    width: float,
    height: float,
    stroke_width_mm: float,
    stroke_color: str,
    stroke_opacity: float,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    path_markup = "\n".join(
        f'    <path d="{svg_path(points)}" />' for points in paths if len(points) > 1
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}mm" height="{height:.0f}mm" viewBox="0 0 {width:.3f} {height:.3f}">
  <g fill="none" stroke="{stroke_color}" stroke-width="{stroke_width_mm:.3f}" stroke-opacity="{stroke_opacity:.3f}" stroke-linecap="round" stroke-linejoin="round">
{path_markup}
  </g>
</svg>
"""
    output_path.write_text(svg, encoding="utf-8")


def main() -> None:
    args = parse_args()
    paths = build_paths(args)
    write_svg(
        paths,
        args.width_mm,
        args.height_mm,
        args.stroke_width_mm,
        args.stroke_color,
        args.stroke_opacity,
        args.output,
    )
    print(f"Wrote {len(paths)} paths to {args.output}")


if __name__ == "__main__":
    main()
