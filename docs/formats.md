# Inputs, outputs and exit status

## Inputs

Use **UTF-8**, optionally with a leading byte-order mark. CRLF, CR and LF are accepted. Each file may contain up to 8 MiB and 50,000 records. Times range from zero through 99:59:59,999. A cue is one timed block of subtitle text.

**SRT.** Separate blocks with a blank line. Use a numeric ID of 1–9 digits, a line of the form `00:00:01,250 --> 00:00:02,500`, then one or more nonblank text lines. Formatting tags are preserved as literal input. Only comma-based millisecond timestamps are supported. A source position is the block's 1-based ordinal. Duplicate numeric IDs, nonsequential IDs, overlaps, and unordered starts are allowed. The output uses fresh consecutive IDs, in start-time order with source order as the tiebreaker. An empty SRT is a valid silent track. A file with no retained cues yields a zero-byte captions.srt; some media players require omission of an empty track.

**Keep CSV.** Without a header, each nonempty row is `start,end` or `start,end,label`. LosslessCut seconds CSV may begin with `Start,End,Name` and additional tag columns. Its data rows must match the header width. Tag values and labels are ignored. The header is shared with the frames exporter; choose seconds when exporting. Boundaries are **source seconds**, with up to 24 decimal digits; half milliseconds round upward once on input. Quote labels containing commas. An empty first start means zero; empty final end needs `--duration SECONDS`. With duration supplied, all input ranges and cues must fit the source. The literal `undefined` emitted for an open boundary is accepted in a LosslessCut headered file. Clock strings, reversed ranges, overlaps, open-ended markers, speed changes, reordering, gaps in output, and empty timelines are unsupported. Adjacent ranges merge. A short interval rounding to zero is an error. Do not pass a list of the material you removed.

**Intervals.** A range includes its start and excludes its end. A cue ending at a cut boundary never spills into the following interval. Summing retained source time before each boundary maps it onto the edited timeline. When a cue spans several kept segments, those pieces touch after cutting. The report gives a single target interval and the total milliseconds lost. Dialogue accuracy inside that interval requires human judgment.

## Archive contract, version 1

| Member | Consumer and contents |
| --- | --- |
| captions.srt | Subtitle editors and players. All intact cues plus partial cues only if explicitly requested. |
| review.html | Human reviewer. Static page listing partial cues with source position, SRT ID, old/new times, and lost milliseconds. Contains no scripts, captions, filenames, labels or external resources. |
| review.json | Automation. UTF-8 object with schema_version, partial_policy (omit/include), duration_ms, summary and cues. |

Each record contains `ordinal`, `source_id`, `source_ms` (two integers), `target_ms` (two integers or null), `lost_ms`, `status` (kept/partial/removed), and `output_id` (integer or null). Removed cues have no target; omitted partial cues still have a target for review. Summary counts kept, partial, removed and written. The first three sum to input count. Consumers should accept additional keys and reject unsupported schema major versions.

For the second cue in the example:

```json
{"ordinal":2,"source_id":2,"source_ms":[2000,4000],"status":"partial","target_ms":[2000,3000],"lost_ms":1000,"output_id":null}
```

| Exit | Meaning |
| --- | --- |
| 0 | Successful write, or help/version. Without the review gate a successful bundle may contain partial cues. |
| 2 | Invalid input, arguments, or filesystem error. Existing outputs are preserved. |
| 3 | Successful write with one or more partial cues and `--fail-on-review`. |

If the output already exists, choose a new filename. On a POSIX filesystem without hard-link support, use a local working directory and copy the completed bundle afterward.
