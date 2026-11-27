# Blueprint

**Mission.** Preserve the value of human-written and translated captions when a recording is shortened. **Vision.** A translator should be able to pick up an edited project and identify every caption decision without asking for the original video just to compute timings.

## Processing model

1. The CLI reads two local, size-limited files. The reader validates UTF-8 and normalizes line endings. The format parsers validate SRT timestamps and CSV keep ranges.
2. The timeline index stores each source range, its end, and the cumulative kept time before its start. To map time t, binary-search for the latest range starting at or before t. Add the retained portion of that range to its prefix. With no previous range, the result is zero.
3. Map both ends of a cue. Their difference equals its retained duration. Compare that with its source length to classify it. This also detects internal cuts when *both endpoints* happen to lie in retained material.
4. The writer sorts output cues, assigns stable new IDs, and records their relationship to the originals in a versioned JSON report. It builds a static HTML review sheet from numeric data and a captions file containing preserved Unicode payloads. It publishes the three fixed members in one archive only after ZIP construction succeeds.

For S ranges and C cues the running time is O(S + C log S + C log C) plus text parsing, rendering and compression. Memory grows with input and report size. Files are independent; a batch runner can process one language track at a time against a shared edit list. Each task needs its own output name. See [limits and edge behavior](formats.md).

## Deployment and operating cost

The supported default is a local Python 3.11+ checkout on a workstation or a command-line package in a virtual environment. No service, database, environment file, credentials, hosting subscription or GPU is needed. Incremental service fees for local use are **$0**. Electricity, existing hardware and contributor time are excluded. An existing VPS can run the same command, with its usual compute and storage charges. Batch workers should delete temporary files according to their own retention policy and publish captions only after review.

For isolated Linux jobs, from the repository root build the image, then mount the checkout as a working directory. These POSIX-shell commands run the process as your local user so the exported ZIP has usable ownership.

```sh
docker build -t spliceledger .
docker run --rm --network none --read-only --user "$(id -u):$(id -g)" -v "$PWD:/work" spliceledger /work/examples/lesson.srt /work/examples/keep.csv -o /work/docker-review.zip
```

The initial build requires access to the Python base image. Run-time networking is unnecessary. A production image publisher should select a reviewed base digest and refresh it when security fixes are available. The project provides a Dockerfile and retains no registry or deployment credentials.

## Accessibility and privacy

Use the CLI with a keyboard or shell automation; summaries are text with numeric exit codes. The offline HTML has a document language, meaningful heading, table caption, row and column headers, and a focusable scroll region for narrow screens. The review table includes numeric source positions so a reviewer can locate duplicate original SRT IDs. No colors are required to interpret status. Preserve Burmese and other scripts as supplied; the tool does not normalize or guess word boundaries. Seek feedback from caption users and screen-reader users before expanding the interface.

Original and output words can be sensitive. Reports have timestamps and IDs only. An editor who uses the optional partial-cue inclusion mode may expose cut words if they circulate the draft. Only the archive contains the retained dialogue. [Security model](../SECURITY.md)

## Maintenance boundaries

Keep a single-source, chronological, unit-speed implementation until there are real export fixtures for more advanced timelines. Add optional adapters at the parser boundary. Review dependency alerts monthly and retest timing and output compatibility for each release. Measure report size and memory before raising input caps. A future streaming report, WebVTT adapter or native auto-editor reader should earn its complexity through documented user workflows. [Roadmap](../ROADMAP.md)
