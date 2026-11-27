"""Bounded, explicit input formats. All times become integer milliseconds."""

import csv
import io
import re
import stat
from dataclasses import dataclass
from pathlib import Path

MAX_BYTES = 8 * 1024 * 1024
MAX_RECORDS = 50_000
MAX_MS = 359_999_999  # 99:59:59,999
STAMP = r"([0-9]{2}):([0-5][0-9]):([0-5][0-9]),([0-9]{3})"
TIMING = re.compile(rf"{STAMP}[ \t]+-->[ \t]+{STAMP}")
BLOCK_BREAK = re.compile(r"\n[ \t]*\n(?:[ \t]*\n)*")
SECONDS = re.compile(r"([0-9]{1,6})(?:\.([0-9]{1,9}))?")


class InputError(ValueError):
    """A data error that can be reported directly to the user."""


@dataclass(frozen=True, slots=True)
class Cue:
    source_id: int
    start: int
    end: int
    text: str


def read_text(path: Path) -> str:
    if not stat.S_ISREG(path.stat().st_mode):
        raise InputError("input must be a regular file")
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise InputError("input exceeds the 8 MiB limit")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise InputError("input must be UTF-8; convert its encoding first") from error
    if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", text):
        raise InputError("input contains unsupported control characters")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def milliseconds(parts: tuple[str, ...]) -> int:
    hours, minutes, seconds, millis = map(int, parts)
    return ((hours * 60 + minutes) * 60 + seconds) * 1000 + millis


def stamp(ms: int) -> str:
    seconds, fraction = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{fraction:03}"


def parse_srt(text: str) -> list[Cue]:
    cues = []
    # Drop trailing blank lines while preserving spaces on the last payload line.
    last_line_end = text.find("\n", len(text.rstrip(" \t\n")))
    body = (text if last_line_end < 0 else text[:last_line_end]).lstrip(" \t\n")
    if not body.strip():
        return cues
    for ordinal, block in enumerate(BLOCK_BREAK.split(body, maxsplit=MAX_RECORDS), 1):
        if ordinal > MAX_RECORDS:
            raise InputError("more than 50000 subtitle cues")
        lines = block.split("\n", 2)
        if (
            len(lines) != 3
            or not re.fullmatch(r"[0-9]{1,9}", lines[0].strip())
            or not lines[2].strip()
        ):
            raise InputError(f"cue {ordinal}: expected numeric ID, timing and text")
        match = TIMING.fullmatch(lines[1].strip())
        if match is None:
            raise InputError(f"cue {ordinal}: expected HH:MM:SS,mmm --> HH:MM:SS,mmm")
        parts = match.groups()
        start, end = milliseconds(parts[:4]), milliseconds(parts[4:])
        if end <= start:
            raise InputError(f"cue {ordinal}: end must follow start")
        cues.append(Cue(int(lines[0]), start, end, lines[2]))
    return cues


def seconds_ms(value: str) -> int:
    """Parse decimal seconds; round exactly half a millisecond upward."""
    match = SECONDS.fullmatch(value.strip())
    if match is None:
        raise InputError(
            "expected nonnegative decimal seconds with up to 9 decimal places"
        )
    digits = (match[2] or "").ljust(4, "0")
    result = int(match[1]) * 1000 + int(digits[:3]) + int(digits[3] >= "5")
    if result > MAX_MS:
        raise InputError("time exceeds 99:59:59,999")
    return result


def parse_keeps(text: str, duration: int | None = None) -> list[tuple[int, int]]:
    """Read seconds-based, headerless keep ranges; coalesce touching ranges."""
    keeps: list[tuple[int, int]] = []
    reader = csv.reader(io.StringIO(text), strict=True)
    count = 0
    try:
        for row in reader:
            if not row:
                continue
            count += 1
            if count > MAX_RECORDS:
                raise InputError("more than 50000 keep ranges")
            if len(row) not in (2, 3):
                raise InputError("expected start,end or start,end,label")
            left, right = (field.strip() for field in row[:2])
            start = 0 if not left and not keeps else seconds_ms(left)
            if right:
                end = seconds_ms(right)
            elif duration is not None:
                end = duration
            else:
                raise InputError("open end requires --duration in source seconds")
            if end <= start:
                raise InputError("empty or reversed range after millisecond rounding")
            if duration is not None and end > duration:
                raise InputError("keep end exceeds source duration")
            if keeps and start < keeps[-1][1]:
                raise InputError("keep ranges must be chronological and cannot overlap")
            if keeps and start == keeps[-1][1]:
                keeps[-1] = (keeps[-1][0], end)
            else:
                keeps.append((start, end))
    except (csv.Error, InputError) as error:
        raise InputError(f"keep list line {reader.line_num}: {error}") from error
    if not keeps:
        raise InputError("empty keep list; supply at least one retained range")
    return keeps
