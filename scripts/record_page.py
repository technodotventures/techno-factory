#!/usr/bin/env python3
"""record_page — record a browser session to video (webm + mp4 + gif).

Factory evidence tool: turn a UI bug/fix repro into a reviewable recording.

Usage:
  PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright \
    $HOME/shots-venv/bin/python scripts/record_page.py <url> <out_dir> \
    [--seconds 8] [--scrolls 3] [--size 1440x900]

Notes:
  - For real bug/fix evidence, prefer a Playwright *test* with
    record_video_dir per context (fails before → passes after), then upload
    both recordings as Coffee artifacts (kind: "recording").
  - This script is the quick interactive pass (walkthroughs, demos).
"""
import argparse
import datetime
import pathlib
import subprocess
import sys

from playwright.sync_api import sync_playwright


def ffmpeg(args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("out_dir")
    ap.add_argument("--seconds", type=float, default=8.0)
    ap.add_argument("--scrolls", type=int, default=3)
    ap.add_argument("--size", default="1440x900")
    args = ap.parse_args()

    width, height = (int(x) for x in args.size.split("x"))
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = out_dir / ".raw"
    raw_dir.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": width, "height": height},
            record_video_dir=str(raw_dir),
            record_video_size={"width": width, "height": height},
        )
        page = ctx.new_page()
        page.goto(args.url, wait_until="load", timeout=30000)
        page.wait_for_timeout(1200)
        pause = max(250, int(args.seconds * 1000 / (args.scrolls + 2)))
        for _ in range(args.scrolls):
            page.mouse.wheel(0, height)
            page.wait_for_timeout(pause)
        page.wait_for_timeout(int(args.seconds * 1000))
        video = page.video
        ctx.close()
        assert video is not None, "no video captured"
        src = pathlib.Path(video.path())
        browser.close()

    webm = out_dir / f"{stamp}.webm"
    src.replace(webm)
    mp4 = out_dir / f"{stamp}.mp4"
    gif = out_dir / f"{stamp}.gif"
    ffmpeg(["-i", str(webm), "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "23", "-movflags", "+faststart", str(mp4)])
    ffmpeg(["-i", str(webm), "-vf", "fps=10,scale=800:-1:flags=lanczos", "-loop", "0", str(gif)])
    print(f"webm: {webm}")
    print(f"mp4:  {mp4}")
    print(f"gif:  {gif}")


if __name__ == "__main__":
    sys.exit(main())
