"""Command-line entry point."""

import argparse
import sys
from pathlib import Path

from . import __version__
from .bundle import publish_bundle, render
from .formats import InputError, parse_keeps, parse_srt, read_text, seconds_ms
from .timeline import Timeline, reconcile


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Retime external SRT captions after chronological cuts."
    )
    parser.add_argument("captions", type=Path, help="source subtitles in UTF-8 SRT")
    parser.add_argument(
        "keeps", type=Path, help="CSV of retained source ranges in decimal seconds"
    )
    parser.add_argument(
        "-o", "--output", required=True, type=Path, help="new ZIP bundle path"
    )
    parser.add_argument(
        "--duration",
        metavar="SECONDS",
        help="source duration for an open-ended final range",
    )
    parser.add_argument(
        "--include-partial",
        action="store_true",
        help="include unedited words from partially cut cues",
    )
    parser.add_argument(
        "--fail-on-review",
        action="store_true",
        help="return status 3 after writing if any cue is partial",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    args = parser.parse_args(argv)
    try:
        duration = seconds_ms(args.duration) if args.duration is not None else None
        timeline = Timeline(parse_keeps(read_text(args.keeps), duration))
        cues = parse_srt(read_text(args.captions))
        if duration is not None and any(cue.end > duration for cue in cues):
            raise InputError("subtitle end exceeds the specified source duration")
        files, summary = render(
            reconcile(cues, timeline), timeline.duration, args.include_partial
        )
        publish_bundle(args.output, files)
    except FileExistsError:
        print("error: output already exists; choose a new filename", file=sys.stderr)
        return 2
    except (InputError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(
        f"{summary['written']} written, {summary['partial']} need review, {summary['removed']} removed."
    )
    return 3 if args.fail_on_review and summary["partial"] else 0
