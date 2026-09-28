# Bounded acquisition diagnosis — 28 September 2026

**Result:** this continuation separates useful code repair from acquisition of an
investigation procedure. The existing learner can repair limit-zero behavior.
A new correction-trained adapter can repair the strict boolean filter when given
a recorded three-turn prefix, but fails to reach that repair autonomously and
never performs the taught mixed-type probe. Four further updates change its
autonomous behavior to repeated probes without repair. Thus useful autonomous
acquisition, retention and fresh transfer remain unestablished.

All 12 maintenance episodes are **development evidence**, not fresh confirmation
or independent histories. No result below is an official benchmark score. The
original pilot, scores and failures are untouched. Starting study revision:
`121242ca597c607f06d9f9084d88b1fa90a458ff`.

| Development comparison | Ordinary base | Adapted learner | Behavioral qualification |
|---|---:|---:|---|
| Original rename teaching repair | 16/18 | 16/18 (pilot adapter) | Neither repaired field-name normalization; adapted edits targeted row values instead. |
| Original limit-zero teaching repair | 18/18 | 18/18 (pilot adapter) | Both repaired code and passed six public tests; neither ran a successful targeted probe. |
| Reviewer-exposed strict filter repair | 9/18 | 13/18 (pilot adapter) | Base did not edit; adapted truthy repair still violated boolean-only contract. |
| Filter after executed correction, fresh process | 9/18 | 9/18 (28 new updates) | Adapted model looped on reads; neither edited. |
| Filter from injected three-turn prefix | 9/18 | 18/18 (28 new updates) | Adapted strict edit passed public tests, but no probe and no finish; coached conditional repair only. |
| Filter after one on-policy bridge correction | 9/18 | 9/18 (32 new updates total) | Adapted model made seven application-successful probes, all with failed assertions, and no edit. |

Scores refer to [18 external development checks](evaluation.json), with the six
public tests also evaluated. Passing these bounded checks is not proof of every
ETL contract. The [behavior audit](analysis.json) separately records source edits,
application-successful probes, assertions, history retrieval, malformed actions
and completion declarations. No executed maintenance run retrieved history or
passed a probe assertion. Repeated deterministic base filter runs are not
independent evidence. The ordinary policy's action failures also mean this is
not yet a demonstrated competent-reference transfer comparison.

## What was changed and learned

The shared interface strictly rejects composite/truncated JSON, permits
paginated source/history reads, expands output from 384 to 1024 tokens, and
reports application success separately from optional expected-output assertions.
It explicitly warns about truthy nonbooleans. These bundled changes and the
warning were supplied to both arms; their individual effects were not isolated.
There were **zero output-cap hits** across this continuation. Strict parsing
prevented silent edit skipping, but a larger cap did not remove malformed short
actions, incorrect schemas or read loops. This does not explain every old branch
failure or prove that output limits never matter.

The first training branch replayed the pilot-adapted learner's actual first
three filter turns, then replaced its truthy edit with an investigator-authored
mixed-type probe, strict edit, repeat probe, public suite and finish. The probe
failed before the edit and passed afterward; the teacher's resulting program
passed all external checks. Seven targets comprised two real successful learner
read actions plus five authored continuation actions. A **new adapter initialized
from base**, rather than the pilot adapter, received 28 updates. This cross-policy
prefix and multi-turn correction branch are disclosed; they are not a replication
of single-turn-only correction.

From a fresh process the resulting learner read repeatedly without editing.
From the exact taught correction context it read once more, applied `is True`,
ran the public suite, and read repeatedly again. The first conditional prompt
was byte-identical to the taught probe prompt; supplying it did not elicit the
probe. The evidence supports conditional semantic repair, not acquisition of the
full taught procedure. Lower teacher-forced loss cannot substitute for this
rollout result.

The final intervention used the **new adapter's own** fresh-session turn-2 read
context. The investigator replaced that read with the previously executed probe,
executed the target in the same source state, and trained that one row four times,
initializing from the 28-update adapter. This prospective development amendment
used the remaining four updates of the original budget. It moved initial behavior
toward probing, but the learner invented a schema, partially repaired its probes,
then repeated a comparison with an incorrect expected-output structure. All eleven
probe assertions failed; it never inspected or edited source. This narrows the
problem beyond merely choosing a tool name. It does not identify one universal
cause or show that the model cannot learn under another method.

## Evidence, state and parity

- [Protocol and adaptive decisions](../../protocol/continuation-v2.md),
  [environment/model hashes](environment.json), [method inspection](../../sources/continuation-02/README.md).
- [Original six-run diagnosis](initial-diagnosis.json), [all raw runs](runs/),
  [frozen submitted programs](runs/), and [evaluation](evaluation.json).
- [Executed correction lineage](correction/lineage.json), [training targets](correction/training.jsonl),
  [teacher checks](correction/evaluation.json), [28-update training](correction-adapter/summary.json).
- [On-policy bridge lineage](bridge/lineage.json), [executed target](bridge/executed-target.json),
  [four-update training](bridge-adapter/summary.json).
- [Matched artifact and cost audit](analysis.json), [expanded history manifest](history-manifest.json),
  [final history manifest](bridge-history-manifest.json).
- [28-update load/reset verification](isolation.json), [32-update verification](bridge-isolation.json),
  [parser/evaluator controls](harness-validation.json).

Each episode runs in a new OS process and isolated workspace. Base weights and
optional adapter are freshly loaded; no conversation or supplied KV cache survives.
Filesystem/model caches remain available. Both arms receive identical initial
code, public tests, task text and full eligible teaching/attempt records. The
analysis verifies those hashes and that evaluated code equals the frozen submission.
Teacher-forced delivery to training differs from ordinary pull-based access and
is part of the treatment. Ordinary history includes executable repaired answers,
not merely summaries. External examiner results and the future requirement are
excluded. The tool API constrains paths; this is not claimed to be an OS filesystem
sandbox for arbitrary malicious participant code. No hidden-file access occurred
in the recorded actions or submitted code.

Both adapter load/reset checks compare actual base outputs before load with
outputs after restoration, verify live learned-state hashes and unchanged base
weights, and observe at least one changed output under adaptation. All checks
passed. The model's original manifest was rehashed successfully. The remote
endpoint returned model metadata; its queried training route returned 404. No
remote inference or training job was needed, and metadata availability is not
claimed as mutable-state access.

## Costs and stopping boundary

The phase used 12 maintenance episodes, 135 generated actions, 396,996 prompt
tokens and 7,694 completion tokens. Episode wall time was 551.92 seconds; the two
training jobs used 129.16 seconds and 32 updates, peaking at 13,086,098,982 MLX
bytes. State-probe costs are separate in the analysis. There were six executed
teacher action slots across the two corrections (four distinct JSON actions),
two learner-authored training targets, and eight total training rows across jobs.
Investigator/teacher token and monetary costs are unknown; examiner/preparation
work is not comprehensively timed. Prior pilot costs are preserved separately.
No new paid participant API calls were made. These native units are not a claim
of cost parity or resource repayment.

Stop this phase on **explanatory progress and a demonstrated local acquisition
limitation**, not a claimed neural win or exhausted hardware. The episode/update
budget is complete; GPU time remained far below the 90-minute ceiling. The best
next experiment is to develop reliable action/feedback use from the actual failed
read/probe states, potentially changing the model/interface or supervising action
choice and feedback interpretation explicitly, then establish autonomous complete
acquisition before transfer. Merely adding more copies of this long JSON target
or more inference turns is not justified by the current evidence.

A nine-case authored subsequent `reject` extension and passing reference were
prepared outside participant access. They remain **unevaluated**; see
[frozen candidate](fresh-freeze.json) and [status](fresh-freeze-status.json).
No fresh-transfer claim is made. CC1 remains unresolved; CC2 and CC3 remain
untested. Full source parity is now checked, but the intended learned procedure
is still missing and no resource-repayment comparison is warranted.

## Reproduction

Use `uv sync --extra adaptation`, the model pin in `environment.json`, and a Mac
with Metal access. All model files are read-only; all modifications are owned here.
Run in a **separate disposable reproduction checkout**, with this phase's output
directory absent, preserving the published evidence elsewhere. The scripts refuse
to overwrite episode/training outputs. Restore the model at the documented sibling
path (or a read-only symlink at that path inside the reproduction layout).

Sequence: create `evidence/continuation-02`, then run
`continuation_prepare.py`, `continuation_validate.py`, `continuation_batch.py`,
`continuation_correct.py`; train with `continuation_train.py --model
../weight-consolidation/models/qwen3-4b-4bit --training
evidence/continuation-02/correction/training.jsonl --output
evidence/continuation-02/correction-adapter --epochs 4 --seed 17`.
Run `continuation_history.py` and `continuation_pair.py`. Run `continuation_conditional.py --prepare` followed by
`continuation_conditional.py`. Run `continuation_bridge.py` and
`continuation_bridge_history.py`; train the bridge with the same training entry
point, bridge paths, `--epochs 4 --seed 17 --initial-adapter
evidence/continuation-02/correction-adapter/adapter.safetensors`. Finish with
`continuation_bridge_pair.py` and `continuation_report.py`.

Run Python commands through `uv run --no-sync python scripts/...`.
`UV_CACHE_DIR=/tmp/egi-uv-cache` was used because the default cache was sandbox
restricted. GPU calls required authorized sandbox escalation. No unpublished
researcher reasoning or external examiner solution is needed to replay the saved
participants and corrections. Fresh extension preparation is optional and is
not part of any reported participant score.
