import json
import os
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from spliceledger.bundle import publish_bundle

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / "export.zip"

    def cli(self, *extra, output=None, captions=None):
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "spliceledger",
                captions or EXAMPLES / "lesson.srt",
                EXAMPLES / "keep.csv",
                "-o",
                output or self.output,
                *extra,
            ],
            cwd=ROOT,
            capture_output=True,
            check=False,
            text=True,
        )

    def test_demo_bundle(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        with ZipFile(self.output) as z:
            self.assertEqual(
                z.namelist(), ["captions.srt", "review.json", "review.html"]
            )
            self.assertIsNone(z.testzip())
            srt = z.read("captions.srt").decode()
            self.assertIn("မင်္ဂလာပါ။", srt)
            self.assertIn("00:00:03,500 --> 00:00:05,500", srt)
            self.assertNotIn("chair", srt)
            data = json.loads(z.read("review.json"))
            self.assertEqual(
                data["summary"], {"kept": 2, "partial": 1, "removed": 1, "written": 2}
            )
            self.assertEqual(data["cues"][1]["lost_ms"], 1000)
            html = Structure()
            html.feed(z.read("review.html").decode())
            tags = [t for t, _ in html.tags]
            self.assertTrue({"title", "main", "h1", "caption", "thead"} <= set(tags))
            self.assertIn(("html", {"lang": "en"}), html.tags)
            self.assertIn(("th", {"scope": "row"}), html.tags)
            self.assertFalse({"script", "img", "iframe", "link"} & set(tags))

    def test_review_gate_and_opt_in(self):
        result = self.cli("--fail-on-review", "--include-partial")
        self.assertEqual(result.returncode, 3, result.stderr)
        with ZipFile(self.output) as z:
            self.assertIn(b"crosses a cut", z.read("captions.srt"))
            self.assertNotIn(b"chair", z.read("captions.srt"))

    def test_no_review_gate_success(self):
        source = Path(self.temp.name) / "empty.srt"
        source.write_bytes(b"")
        self.assertEqual(self.cli("--fail-on-review", captions=source).returncode, 0)

    def test_repeatable_and_no_overwrite(self):
        self.assertEqual(self.cli().returncode, 0)
        contents = self.output.read_bytes()
        self.assertEqual(self.cli("--include-partial").returncode, 2)
        other = self.output.with_name("another.zip")
        self.assertEqual(self.cli(output=other).returncode, 0)
        self.assertEqual(other.read_bytes(), contents)
        self.assertEqual(self.output.read_bytes(), contents)

    def test_bad_input_no_output(self):
        source = Path(self.temp.name) / "bad.srt"
        source.write_bytes(b"\xff")
        for result in (
            self.cli(captions=source),
            self.cli("--duration", "1"),
            self.cli(captions=source.with_name("missing")),
        ):
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(self.output.exists())

    def test_concurrent_writers(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.cli().returncode, range(2)))
        self.assertEqual(sorted(results), [0, 2])
        self.assertEqual(list(self.output.parent.glob(".spliceledger-*")), [])

    @unittest.skipIf(
        os.name == "nt", "Windows symlink creation may need special privileges"
    )
    def test_existing_symlink_is_preserved(self):
        target = self.output.with_name("missing")
        self.output.symlink_to(target)
        self.assertEqual(self.cli().returncode, 2)
        self.assertTrue(self.output.is_symlink())
        self.assertFalse(target.exists())

    def test_archive_failure_cleanup(self):
        with (
            patch(
                "spliceledger.bundle.ZipFile.writestr", side_effect=OSError("disk full")
            ),
            self.assertRaises(OSError),
        ):
            publish_bundle(self.output, {"captions.srt": "x"})
        self.assertEqual(list(self.output.parent.iterdir()), [])
