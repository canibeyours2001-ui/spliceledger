# Adoption and maintenance

**Repository description.** Retime external SRT subtitles after video cuts and flag captions that need a human review. Offline Python CLI, with a LosslessCut CSV workflow.

**Topics.** accessibility, captions, subtitles, srt, losslesscut, localization, burmese, python, command-line, offline-first, video-editing. Keep “retime SRT after cutting a video” and the input/output example visible in the README for people searching for the problem.

## First contributors

Start with the bilingual example. Reproduce its four source decisions, then run the tests in [CONTRIBUTING](../CONTRIBUTING.md). Proposed good first issues:

1. **Document a real LosslessCut CSV round trip.** Use a synthetic clip, capture the version and export settings, record requested vs actual export boundaries, and contribute the small CSV. Acceptance: an independent editor can reproduce the file, understand keyframe behavior and run the CLI.
2. **Check the review sheet with VoiceOver or NVDA.** Use the shipped example. Record OS/reader versions, whether column and row headings announce correctly, and how you located the affected cue. Acceptance: reproducible observations without sharing a personal recording.
3. **Contribute a right-to-left caption fixture.** Create a short original bilingual example with punctuation. Acceptance: visible text and logical code-point order survive the round trip and an actual reader reviews the example.

## Feedback and outreach

After release, ask invited editors and translation volunteers to try one real edit on their own device. Share a small demo and link to a reproducible case in relevant captioning or LosslessCut communities only where community rules permit and the link answers an existing question. Ask upstream maintainers whether a recipe or adapter would be preferable to a separate integration. Do not mass-post or request production recordings.

**Launch announcement draft:** “When you cut a talk after its subtitles have been translated, which lines still match? SpliceLedger retimes the complete lines and marks exactly where an editor should listen again. Try the included Burmese-English example with Python. We'd like feedback from anyone already exchanging SRT files after an edit.”

## Measures, funding and release process

| Indicator | Measurement with consent |
| --- | --- |
| Actual adoption | Independent projects or editors reporting a second use within 30 days. Count projects once. |
| Review time | Record paired minutes before/after for comparable edits and cue counts; report sample size and range. |
| Caption quality | Have a reviewer listen to partial-cue intervals. Count missed restored words, incorrect retained words, and timing mismatches. |
| Compatibility | Count exporter/version combinations with a reproducible test fixture, and distinguish fixtures from self-reported usage. |
| Maintenance | Track time to reproduce timing bugs, number of independent reviewers, and unresolved regressions per release. |

No telemetry is collected. Downloads and stars may signal discovery; neither establishes repeat use. A maintainer can invite GitHub Sponsors or accessibility grants once users report value, with funding directed toward paid caption-user testing, translation and maintenance. Paid integration work is possible; it grants no special veto over the public format or roadmap. No sponsors or income are claimed.

The owner triages monthly, checks dependency updates and security reports, and publishes changes only after the documented tests pass. Before tagging a version, align both version declarations, update the changelog, build the sdist/wheel, run the demo outside the checkout, and inspect archive contents. Use semantic versioning; discuss breaking CLI or JSON changes in an issue with a migration example. GitHub source releases are sufficient until maintainers can support trusted package-index publishing. If the maintainer steps down, invite a successor through a public issue and document the handover.
