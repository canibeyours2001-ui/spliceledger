import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from spliceledger.formats import (
    InputError,
    parse_keeps,
    parse_srt,
    read_text,
    seconds_ms,
    stamp,
)


class FormatTests(unittest.TestCase):
    def test_decimal_rounding(self):
        for text, result in [
            ("0.000499999", 0),
            ("0.03336666666666667", 33),
            ("0.00050", 1),
            ("1.9999", 2000),
            ("359999.999", 359999999),
            ("00", 0),
        ]:
            self.assertEqual(seconds_ms(text), result)
        self.assertEqual(stamp(359999999), "99:59:59,999")

    def test_bad_seconds(self):
        for value in (
            "NaN",
            "inf",
            "-1",
            "1e8",
            "1." + "9" * 25,
            "360000",
            "၃",
            "9" * 1000,
        ):
            with self.subTest(value=value), self.assertRaises(InputError):
                seconds_ms(value)

    def test_keep_label_commas_and_open_ends(self):
        self.assertEqual(
            parse_keeps(',1,"a,b"\n1,2,x\n3,,last\n', 4000), [(0, 2000), (3000, 4000)]
        )

    def test_invalid_keep_list(self):
        for sample in (
            "",
            "start,end,label",
            "0,0",
            "3,2",
            "0,1\n0.5,2",
            '0,1,"unclosed',
            "0,0.0003",
            "1,",
            "0,1\n,2",
            "0,1,2,3",
        ):
            with self.subTest(sample=sample), self.assertRaises(InputError):
                parse_keeps(sample)

    def test_losslesscut_export_header_tags_and_open_bounds(self):
        text = (
            'Start,End,Name,Speaker\nundefined,0.03336666666666667,"hi, there",A\n'
            "1.001,undefined,,B\n"
        )
        self.assertEqual(parse_keeps(text, 2000), [(0, 33), (1001, 2000)])
        for invalid in (
            "Start,End,Name,Speaker\n0,1,name",
            "Start,End,Name\n",
            "Start,End,Name\nStart,End,Name\n0,1,cue",
        ):
            with self.subTest(invalid=invalid), self.assertRaises(InputError):
                parse_keeps(invalid)

    def test_duration_and_record_limits(self):
        with self.assertRaises(InputError):
            parse_keeps("0,3", 2000)
        with patch("spliceledger.formats.MAX_RECORDS", 1):
            with self.assertRaises(InputError):
                parse_keeps("0,1\n1,2")
            block = "7\n00:00:00,000 --> 00:00:01,000\nx"
            with self.assertRaises(InputError):
                parse_srt(block + "\n\n" + block)

    def test_srt_text_preservation(self):
        text = "\n  9\n00:00:00,000 --> 00:00:01,000\n  မြန်မာ  \n 👋  \n \n"
        (cue,) = parse_srt(text)
        self.assertEqual((cue.source_id, cue.text), (9, "  မြန်မာ  \n 👋  "))
        self.assertEqual(parse_srt(" \n "), [])

    def test_bad_srt(self):
        for body in (
            "x",
            "1\n00:00:00,000 --> 00:00:01,000\n ",
            "A\n00:00:00,000 --> 00:00:01,000\nx",
            "1\n00:60:00,000 --> 00:61:00,000\nx",
            "1\n00:00:01,000 --> 00:00:01,000\nx",
            "1\n00:00:00,000 --> 00:00:02,000 position:1\nx",
        ):
            with self.subTest(body=body), self.assertRaises(InputError):
                parse_srt(body)

    def test_bytes_controls_and_bounds(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input"
            path.write_bytes(b"\xef\xbb\xbf1\r\n2\r3")
            self.assertEqual(read_text(path), "1\n2\n3")
            for invalid in (b"\xff", b"ok\x00", b"ok\x1b"):
                path.write_bytes(invalid)
                with self.assertRaises(InputError):
                    read_text(path)
            with (
                patch("spliceledger.formats.MAX_BYTES", 1),
                self.assertRaises(InputError),
            ):
                read_text(path)
            with self.assertRaises(InputError):
                read_text(Path(directory))
