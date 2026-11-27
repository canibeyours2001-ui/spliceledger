import json
import random
import unittest

from spliceledger.bundle import render
from spliceledger.formats import Cue
from spliceledger.timeline import Timeline, reconcile


class TimelineTests(unittest.TestCase):
    def test_boundary_cases(self):
        tl = Timeline([(2, 4), (6, 9)])
        cases = [
            (0, 2, "removed", 0, 0),
            (4, 6, "removed", 2, 2),
            (2, 4, "kept", 0, 2),
            (1, 3, "partial", 0, 1),
            (2, 9, "partial", 0, 5),
            (7, 12, "partial", 3, 5),
            (9, 12, "removed", 5, 5),
        ]
        for start, end, status, left, right in cases:
            (d,) = reconcile([Cue(8, start, end, "hello")], tl)
            self.assertEqual((d.status, d.start, d.end), (status, left, right))

    def test_random_against_independent_clock(self):
        rng = random.Random(32831)
        for _ in range(200):
            bounds = sorted(rng.sample(range(80), 10))
            spans = list(zip(bounds[::2], bounds[1::2]))
            tl = Timeline(spans)
            ticks = {t for a, b in spans for t in range(a, b)}
            expected = [sum(t < point for t in ticks) for point in range(85)]
            self.assertEqual([tl.project(p) for p in range(85)], expected)
            self.assertEqual(tl.duration, len(ticks))

    def test_invalid_timeline(self):
        for spans in ([], [(-1, 0)], [(2, 1)], [(0, 3), (1, 4)]):
            with self.assertRaises(ValueError):
                Timeline(spans)

    def test_overlay_order_and_non_unique_ids(self):
        cues = [
            Cue(9, 300, 500, "late"),
            Cue(9, 0, 400, "early"),
            Cue(0, 0, 200, "other"),
        ]
        files, counts = render(reconcile(cues, Timeline([(0, 500)])), 500, False)
        rows = json.loads(files["review.json"])["cues"]
        self.assertEqual([row["output_id"] for row in rows], [3, 1, 2])
        self.assertEqual(counts["written"], 3)

    def test_reports_contain_no_dialogue_or_label(self):
        cue = Cue(8, 0, 2000, "<b>PRIVATE & PERSONAL</b>")
        decisions = reconcile([cue], Timeline([(0, 1000)]))
        default, _ = render(decisions, 1000, False)
        opt_in, _ = render(decisions, 1000, True)
        self.assertEqual(default["captions.srt"], "")
        self.assertIn(cue.text, opt_in["captions.srt"])
        for name in ("review.html", "review.json"):
            self.assertNotIn("PRIVATE", opt_in[name])

    def test_all_removed_and_empty(self):
        for cues in ([], [Cue(1, 0, 20, "deleted")]):
            files, summary = render(reconcile(cues, Timeline([(30, 50)])), 20, False)
            self.assertEqual(summary["written"], 0)
            self.assertEqual(files["captions.srt"], "")
