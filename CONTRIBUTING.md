# Contribute

Run `python3 -m unittest discover -s tests -v` from a checkout with Python 3.11 or newer. The runtime and core tests use the standard library. Installing FFmpeg adds a generated-audio integration test. Use invented captions that you have the right to license.

Start with the [example](examples/lesson.srt) and the [format contract](docs/formats.md). To reproduce a report, run the example in the README and compare its source positions with the cut list. The parser is in `formats.py`, the timing math in `timeline.py`, output generation in `bundle.py`, and command-line handling in `cli.py`.

## Changes and decisions

Open an issue before implementing a new format or changing default caption inclusion. A proposal needs a real exporter, a rights-cleared sample, and a test that distinguishes the new behavior. Small bug fixes and documentation improvements can go straight to a pull request. Include reproduction steps and tests for the case you fixed. By submitting work, you agree to distribute it under the repository's Apache-2.0 license.

The repository owner reviews and merges changes. Timing changes require agreement on examples before merging. Any contributor can propose becoming a reviewer after several reviewed contributions. Maintainers record scope or compatibility decisions in the issue, including alternatives and objections. For a disputed change, keep existing behavior until a second reviewer or an affected user can reproduce the need.

See the [community plan](docs/community.md) for starter tasks, feedback channels and release checks.
