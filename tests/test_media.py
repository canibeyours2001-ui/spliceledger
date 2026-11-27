"""Optional integration test: measure caption boundaries in PCM audio actually cut by FFmpeg."""

import io
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from zipfile import ZipFile

from spliceledger.formats import parse_srt

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("ffmpeg"), "optional FFmpeg integration")
class MediaTests(unittest.TestCase):
    def test_cut_audio_agrees_with_retimed_captions(self):
        rate = 8000
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, edited = root / "source.wav", root / "edited.wav"
            zip_path = root / "captions.zip"
            # A synthetic square-wave marker occupies the source's last cue.
            with wave.open(str(source), "wb") as wf:
                wf.setparams((1, 2, rate, 0, "NONE", "not compressed"))
                samples = [
                    ((-1) ** (i // 10)) * 800 if 6.5 * rate <= i < 8.5 * rate else 0
                    for i in range(9 * rate)
                ]
                wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))
            subprocess.run(
                [
                    "ffmpeg",
                    "-nostdin",
                    "-loglevel",
                    "error",
                    "-i",
                    str(source),
                    "-filter_complex",
                    (
                        "[0:a]atrim=0:3,asetpts=PTS-STARTPTS[a];"
                        "[0:a]atrim=6:9,asetpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=0:a=1[out]"
                    ),
                    "-map",
                    "[out]",
                    "-c:a",
                    "pcm_s16le",
                    str(edited),
                ],
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "spliceledger",
                    ROOT / "examples/lesson.srt",
                    ROOT / "examples/keep.csv",
                    "-o",
                    zip_path,
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
            )
            with ZipFile(zip_path) as bundle:
                last_cue = parse_srt(bundle.read("captions.srt").decode())[-1]
                duration = json.loads(bundle.read("review.json"))["duration_ms"]
            with wave.open(io.BytesIO(edited.read_bytes())) as wf:
                frames = wf.getnframes()
                self.assertEqual(frames * 1000 // rate, duration)
                values = struct.unpack(f"<{frames}h", wf.readframes(frames))
            active = [i for i, value in enumerate(values) if value]
            self.assertEqual(
                (active[0], active[-1] + 1),
                (last_cue.start * rate // 1000, last_cue.end * rate // 1000),
            )
