"""Project source times onto a single timeline made from retained ranges."""

from bisect import bisect_right
from dataclasses import dataclass

from .formats import Cue


class Timeline:
    """Index validated, chronological keep ranges for fast prefix-length queries."""

    def __init__(self, keeps: list[tuple[int, int]]):
        self.starts = []
        self.ends = []
        self.offsets = []
        self.duration = 0
        for start, end in keeps:
            if start < 0 or end <= start or (self.ends and start < self.ends[-1]):
                raise ValueError("invalid keep range")
            self.starts.append(start)
            self.ends.append(end)
            self.offsets.append(self.duration)
            self.duration += end - start
        if not self.starts:
            raise ValueError("empty timeline")

    def project(self, time: int) -> int:
        """Number of kept milliseconds strictly before this source boundary."""
        i = bisect_right(self.starts, time) - 1
        if i < 0:
            return 0
        return self.offsets[i] + min(time, self.ends[i]) - self.starts[i]


@dataclass(frozen=True, slots=True)
class Decision:
    ordinal: int
    cue: Cue
    start: int
    end: int
    status: str


def reconcile(cues: list[Cue], timeline: Timeline) -> list[Decision]:
    decisions = []
    for ordinal, cue in enumerate(cues, 1):
        start = timeline.project(cue.start)
        end = timeline.project(cue.end)
        kept = end - start
        if kept == 0:
            status = "removed"
        elif kept < cue.end - cue.start:
            status = "partial"
        else:
            status = "kept"
        decisions.append(Decision(ordinal, cue, start, end, status))
    return decisions
