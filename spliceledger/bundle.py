"""Generate a deterministic, self-contained handoff using standard formats."""

import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from .formats import stamp
from .timeline import Decision


def render(decisions: list[Decision], duration: int, include_partial: bool):
    output = sorted(
        (
            d
            for d in decisions
            if d.status == "kept" or (include_partial and d.status == "partial")
        ),
        key=lambda d: (d.start, d.ordinal),
    )
    output_ids = {d.ordinal: i for i, d in enumerate(output, 1)}
    subtitles = "".join(
        f"{i}\n{stamp(d.start)} --> {stamp(d.end)}\n{d.cue.text}\n\n"
        for i, d in enumerate(output, 1)
    )
    counts = Counter(d.status for d in decisions)
    summary = {k: counts[k] for k in ("kept", "partial", "removed")}
    summary["written"] = len(output)
    rows = []
    review_rows = []
    for d in decisions:
        lost = d.cue.end - d.cue.start - (d.end - d.start)
        rows.append(
            {
                "ordinal": d.ordinal,
                "source_id": d.cue.source_id,
                "source_ms": [d.cue.start, d.cue.end],
                "status": d.status,
                "target_ms": [d.start, d.end] if d.start < d.end else None,
                "lost_ms": lost,
                "output_id": output_ids.get(d.ordinal),
            }
        )
        if d.status == "partial":
            review_rows.append(
                f'<tr><th scope="row">{d.ordinal}</th><td>{d.cue.source_id}</td>'
                f"<td>{stamp(d.cue.start)} – {stamp(d.cue.end)}</td>"
                f"<td>{stamp(d.start)} – {stamp(d.end)}</td><td>{lost}</td></tr>"
            )
    policy = "include" if include_partial else "omit"
    report = {
        "schema_version": 1,
        "partial_policy": policy,
        "duration_ms": duration,
        "summary": summary,
        "cues": rows,
    }
    table = (
        "<table><caption>Partially retained cues in source order</caption>"
        '<thead><tr><th scope="col">Source position</th><th scope="col">SRT ID</th>'
        '<th scope="col">Original time</th><th scope="col">Edited time</th>'
        '<th scope="col">Removed milliseconds</th></tr></thead><tbody>'
        + "".join(review_rows)
        + "</tbody></table>"
        if review_rows
        else "<p>No cue crosses a cut.</p>"
    )
    action = (
        "Partial cues are included with their original words. Check each one before sharing the subtitles."
        if include_partial
        else "Partial cues are omitted. Listen at each edited time and add back the words still heard."
    )
    page = f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Caption cut review | SpliceLedger</title>
<style>body{{font:1rem/1.5 system-ui,sans-serif;margin:2rem auto;padding:0 1rem;max-width:70rem}}
table{{border-collapse:collapse}}th,td{{padding:.45rem;text-align:left;border:1px solid currentColor}}
caption{{font-weight:bold;text-align:left}}section{{overflow:auto}}h1{{line-height:1.2}}</style>
<main><h1>Caption cut review</h1><p>{summary["kept"]} intact · {summary["partial"]} partial ·
{summary["removed"]} removed · {len(output)} written to captions.srt.</p><p>{action}</p>
<section tabindex="0" aria-label="Cut review details">{table}</section>
<p>Source position counts cues from 1 in the original file. Times use hours:minutes:seconds,milliseconds.</p>
</main></html>
"""
    files = {
        "captions.srt": subtitles,
        "review.json": json.dumps(report, separators=(",", ":")) + "\n",
        "review.html": page,
    }
    return files, summary


def publish_bundle(path: Path, files: dict[str, str]) -> None:
    """Commit the finished archive without replacing existing files or symlinks."""
    with tempfile.NamedTemporaryFile(
        dir=path.parent, prefix=".spliceledger-", delete=False
    ) as staged:
        temporary = Path(staged.name)
    try:
        with ZipFile(temporary, "w") as archive:
            for name, body in files.items():
                info = ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100600 << 16
                archive.writestr(info, body.encode("utf-8"), compress_type=ZIP_DEFLATED)
        if os.name == "nt":
            os.rename(temporary, path)  # On Windows rename fails if destination exists.
        else:
            os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
