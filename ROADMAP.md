# Roadmap

## 0.1 · Initial implementation

Offline CLI, seconds-based CSV, SRT input and output, versioned JSON, static HTML review, conservative partial-cue handling, sample in Burmese and English, package and container definitions, parser and timeline tests, media integration test.

## 0.2 · Validate whether review saves time

First 30–60 days after launch, subject to available volunteers. Seek three editors who use external captions. For each, collect two anonymous timing comparisons and document cases where following the supplied cut list disagrees with the rendered media. Add rights-cleared fixtures from at least two editor exports. Publish aggregate results only with consent. If reviewers see little benefit, investigate an upstream contribution before expanding the project.

## 0.3 · Choose one requested integration

Pick native auto-editor timeline input, WebVTT, or a subtitle-editor handoff based on repeat requests and real fixtures. Define supported operations, preserve the handoff schema, and reject unsupported edits explicitly. Reordered, speed-adjusted and multi-source timelines require a separate mapping design. Defer until a reviewer can verify source-to-output decisions.

## Toward 1.0

Require a stable report contract, real editor fixtures, supported-OS CI, keyboard and assistive-technology feedback, documented limitations, and a second reviewer able to cut a release. A hosted service or model is outside the current maintenance budget.
