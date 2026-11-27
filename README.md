# SpliceLedger

Keep existing subtitles in sync when you cut a recording. Give SpliceLedger an SRT file and a list of the parts you kept. It writes the retimed subtitles and tells a reviewer exactly where a cut may have changed the meaning of a line.

Suppose a line says **“Turn left after the bridge”** and the edit removes the last two seconds. Timestamps alone cannot tell which words survived. SpliceLedger omits that line from the draft and records where to listen and restore it. Complete lines move automatically. Use it for translated talks, teaching videos, caption QA and silence-cut pipelines. All processing takes place on your device.

## Try the bilingual example

With Python 3.11 or newer, run these commands in Terminal. The first downloads the source; the second opens its directory. The third runs the sample using only Python.

```sh
git clone https://github.com/canibeyours2001-ui/spliceledger.git
cd spliceledger
python3 -m spliceledger examples/lesson.srt examples/keep.csv -o lesson-review.zip
```

Expected output: `2 written, 1 need review, 1 removed.` Open the ZIP in Finder or your archive app. Open **review.html** for the review list, then **captions.srt** in your subtitle editor. Use **review.json** for automation. On Windows, use `py -3` in place of `python3` with a supported Python installed.

| Original source time | After keeping 0–3 s and 6–9 s |
| --- | --- |
| 0.0–1.2 s, Burmese and English greeting | Appears unchanged |
| 2.0–4.0 s, crossing the first cut | Review at 2.0–3.0 s, omitted from draft |
| 4.0–5.0 s, chair noise | Removed |
| 6.5–8.5 s, lesson introduction | Appears at 3.5–5.5 s |

An omitted line leaves a caption gap. Listen to each flagged point and add the words or meaningful sounds still present before publishing. Review the recording to check the supplied cuts match the actual media. Output follows the given edit times exactly. Keyframe-aligned exports can start earlier than the requested times. [LosslessCut FAQ](https://losslesscut.app/docs/faq)

## Use your own file

Export the **kept** segments from your editor as a seconds-based CSV, in playback order. For a silence-removal pipeline, save the retained intervals used by its renderer. If you only have the finished video and no edit list, SpliceLedger cannot infer the cuts. For LosslessCut choose its numeric seconds CSV, and use the actual cut points if the export snapped to keyframes.

```csv
Start,End,Name
0,3,Introduction
6,9,Lesson
```

Run the command with your original subtitles and CSV. Each output filename must be new. Add `--fail-on-review` in automation to get exit code 3 when any cue needs attention. The ZIP is still written. To prepare a private working draft with the original wording of partial cues, pass `--include-partial`. The HTML and JSON reports never include dialogue.

```sh
python3 -m spliceledger original.srt keeps.csv -o draft.zip --fail-on-review
```

## Install the command

From the cloned repository, create an isolated environment and install the package into it. The build can download setuptools. For fully offline use, run the module directly from the checkout as above.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install .
.venv/bin/spliceledger --help
```

On Windows the executable directory is `.venv\Scripts`. Installation from this repository is the supported route. No model, GPU, account, FFmpeg binary or paid API is required for the CLI.

## Scope

Version 0.1 handles plain UTF-8 SRT, multiple languages, overlapping cues, and chronological cuts from a single source at normal speed. It preserves payload text without segmenting words. It does not currently read native auto-editor timelines, cut video, find silence, handle speed changes, or check translation accuracy. For retiming captions while rendering a video, see [auto-editor](https://auto-editor.com/docs/v3). For a browser workflow that accepts EDL/XML, see [Cuescribe](https://cuescribe.app/split-subtitles).

[Input and report contract](docs/formats.md) · [Architecture and deployment](docs/design.md) · [Project selection and evidence](docs/opportunities.md) · [Roadmap](ROADMAP.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [License and dependency inventory](docs/licensing.md)

Licensed under [Apache 2.0](LICENSE).

[Verification results](docs/verification.md) · [Community and adoption plan](docs/community.md)
