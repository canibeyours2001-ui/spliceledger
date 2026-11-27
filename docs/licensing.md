# License choice and inventory

We selected **Apache License 2.0** for the code, documentation and synthetic examples. Pipeline authors can integrate the tool commercially, redistribute it, and build private integrations while preserving the license, required notices, and change notices. Its explicit contributor patent grant and patent-litigation termination terms are useful when several organizations contribute timing and format adapters. This choice accepts that a company may keep its improvements private. The complete [LICENSE](../LICENSE) is the original [Apache Software Foundation text](https://www.apache.org/licenses/LICENSE-2.0.txt).

| Candidate | Commercial use and redistribution | Patent and community trade-off |
| --- | --- | --- |
| MIT | Commercial and closed redistribution allowed; carry copyright and permission notice. | Shortest obligations; no express contributor patent grant in its text. |
| BSD-3-Clause | Commercial and closed redistribution allowed; retain required notices and follow the non-endorsement clause. | Useful name protection; no express contributor patent grant. |
| Apache-2.0 | Commercial and closed redistribution allowed; include license, retain applicable notices, mark modified files, pass through relevant NOTICE attributions if present. | Express contributor patent license and termination; modest extra paperwork for integrators. |
| GPL-3.0-only | Commercial use allowed; conveying a covered combined work generally requires GPL terms and corresponding source obligations. | Patent provisions and strong sharing of distributed derivatives; more friction for proprietary integrations. |
| AGPL-3.0-only | GPL-style redistribution duties; users interacting over a network with a modified version must be offered its corresponding source as specified in section 13. | Patent provisions and coverage of modified hosted services; the core product is a local CLI. |
| MPL-2.0 | Commercial distribution allowed; distributing modified covered files generally requires making their source available under MPL. Separate files may have other terms. | Express patent grant and file-level reciprocity; useful if sharing parser fixes takes priority over minimizing integration duties. |

[Comparison of license conditions](https://choosealicense.com/appendix/) · [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html) · [AGPLv3](https://www.gnu.org/licenses/agpl-3.0.html) · [MPL FAQ](https://www.mozilla.org/en-US/MPL/2.0/FAQ/)

## Checked boundaries for 0.1.0

| Component | Relationship and verification |
| --- | --- |
| Application package | Original Python code, example text and project policies. Packaging metadata declares zero third-party runtime requirements. The built wheel was inspected for distribution files and license contents. No third-party application code is bundled. |
| CPython and standard library | A separately supplied interpreter runs the package. Its components retain their own [Python license terms](https://docs.python.org/3/license.html). The wheel does not redistribute the interpreter. |
| setuptools | Build-time backend only. Installed distribution metadata for 84.2.1 identifies MIT. It does not ship inside the wheel. |
| LosslessCut, auto-editor, Cuescribe | External tools discussed for context. Numeric CSV is a data boundary. No code, UI assets, models or datasets are copied from them. |
| FFmpeg | Optional integration test invokes a separately installed executable on generated audio. The wheel and Dockerfile do not distribute FFmpeg. |
| CI actions and optional container | Actions execute in CI; the application wheel contains none of their code. Container redistribution also includes Python and base OS packages under their own terms; inspect the chosen image and retain upstream notices before publishing an image. |
| User files | The project's license does not grant rights in input recordings, captions or translations; those remain subject to their own terms. |

The official license text matched the repository copy byte-for-byte. SHA-256: `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`. Revisit this inventory before adding runtime packages, vendored files, models, fonts or external fixtures.
