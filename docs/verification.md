# Verification for 0.1.0

Performed on Linux on 27 November 2026. Checks below were run on local synthetic data. For the cross-platform and Docker matrix see the [GitHub Actions runs](https://github.com/canibeyours2001-ui/spliceledger/actions/workflows/ci.yml).

| Check | Observed result |
| --- | --- |
| Automated tests | 23/23 passed separately on CPython 3.12.14 and 3.13.5. Tests cover exact boundaries, nested cuts, overlapping tracks, Unicode, strict encodings, malformed CSV/SRT, limits, existing files/symlinks, concurrent writers and failed-write cleanup. |
| Algorithm cross-check | 200 seeded random timelines compared the indexed mapping to an independently enumerated millisecond clock at 85 points each. |
| Actual media edit | An FFmpeg filter cut a synthetic nine-second recording to six seconds. For the retained audio marker, the first and last sample boundaries matched the retimed caption at 3.500 s and 5.500 s on an 8 kHz clock. |
| LosslessCut interoperability | Parsed all three upstream CSV fixtures from [LosslessCut v3.70.2](https://github.com/mifi/lossless-cut/tree/v3.70.2/src/renderer/src/test/fixtures). Their output durations matched independently summed decimal ranges at 548,567, 750,843 and 397,376 ms. These cover the exporter format; actual cut boundaries still depend on the render. |
| Scale check | A single local run processed 50,000 cues against 50,000 nonadjacent keep ranges in 2.68 s, with peak process RSS of 121,480 KiB. All 50,000 partial decisions were present. Hardware and workload affect these measurements. |
| Packaging | Built the source distribution and wheel. Installed the wheel in a clean environment, ran the CLI outside the checkout and checked dependencies. The documented source-install route also succeeded. Confirmed zero Requires-Dist entries, Apache-2.0 metadata and exact LICENSE bytes in the wheel. |
| Static code checks | Ruff passed. Bandit 1.9.4 reported zero findings and zero skipped security tests in the application package. The source review checked input bounds, public output paths, archive member names and which user data enters HTML/JSON. |
| Advisory check | pip-audit initially found advisories in the virtual environment's old bundled pip 25.0.1. After upgrading it to 26.3, it found no known vulnerabilities in the audited installed package set. It skipped SpliceLedger itself because this version is not on PyPI. The application has zero third-party runtime packages. This was not an audit of the container OS or Python interpreter. |
| Browser accessibility | Chromium at a 360-pixel viewport showed one labeled table, tab focus reached the scrollable details region and the page width stayed at 360 pixels. axe-core 4.14.1 reported zero violations or incomplete checks under its WCAG 2 A/AA and 2.1 A/AA tags on the sample review. |
| Licensing | Compared LICENSE byte-for-byte with the Apache Software Foundation download. Checked build-backend license metadata and archive contents. |

## Reproduce

Run the commands below from the repository root. The first uses the standard library suite; the second runs the sample; the third prints its JSON. Use a fresh output filename on repeated runs.

```sh
python3 -m unittest discover -s tests -v
python3 -m spliceledger examples/lesson.srt examples/keep.csv -o verified.zip
python3 -c "import zipfile; print(zipfile.ZipFile('verified.zip').read('review.json').decode())"
```

## Open validation work

Recruit real editors and assistive-technology users. Test a real LosslessCut GUI export against rendered frame boundaries, especially with keyframe snapping. No hearing-accessibility certification, speech-content accuracy assessment, human screen-reader test, or external adoption measurement is claimed. The FFmpeg fixture uses precise audio sample cuts and does not test video keyframe snapping.
