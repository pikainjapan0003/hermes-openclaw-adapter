# Error Surface Audit — Round 5

Status: completed review; test-only guard added. This report does not authorize
product changes, report persistence, runtime wiring, or disclosure of raw input.

## Scope and method

This round extends the error-surface review to every current repository flow
that renders operational report text: the three-source status table, mirror
drift table, Blackboard inspection summary, and schema Markdown renderer. The
health/coverage research documents are manually reviewed committed artifacts;
the repository contains no product or script function that writes them.

The review distinguishes stdout exposure from filesystem persistence. The
existing 14-xfail redaction baseline remains unchanged: known stdout echoing is
neither hidden nor reclassified here. This round asks the narrower question
required by NIGHT-BATCH-19: can hostile report input be written into a research
file by a current generation flow?

## Findings

| ID | Severity | Result | Evidence |
|---|---|---|---|
| ESR5-01 | — | Pass | No Python source under `app/` or `scripts/` combines a research target with a file-write call. |
| ESR5-02 | — | Pass | All four current renderers return data or print to stdout; a synthetic research destination remains empty after hostile-marker rehearsal. |
| ESR5-03 | P3, carried | Open | Some read-only stdout surfaces still echo caller-controlled labels/details. This is the existing explicit xfail baseline, not a filesystem-write finding. |

## Mechanical guard

`tests/test_research_report_generation_no_leak.py` uses one synthetic secret
marker and one synthetic absolute-path marker. It verifies:

1. neither marker exists in committed research reports;
2. `app/` and `scripts/` have no research-targeted write call;
3. hostile inputs exercised through all four current renderers do not create a
   file in the designated temporary research directory.

The test writes only synthetic inputs beneath pytest `tmp_path`. It does not
write to this repository's research directory, and it does not alter the 14
known xfail cases.
