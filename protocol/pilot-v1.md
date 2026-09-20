# Pilot v1 — ETL investigation procedure acquisition

20 September 2026. This is a bounded development pilot. It is a local
adaptation of the pinned SlopCodeBench ETL sequence, not an official
SlopCodeBench evaluation.

## Target

The learner is trained on compatible tool-use trajectories for a concrete
investigation procedure:

1. inspect the current requirement and source;
2. inspect eligible earlier attempt history when it can resolve uncertainty;
3. run a discriminating public test or probe before editing;
4. apply a narrow source patch;
5. rerun visible tests and a targeted probe; and
6. report completion only after the checks pass.

The acquisition cases are small ETL checkpoint-1 normalization and
checkpoint-2 linear-execution repairs. Transfer is a fresh checkpoint-3-style
branching change. The later requirement and hidden confirmation tests are not
available during acquisition or adapter construction.

## Workload adaptation

The participant workspace contains a researcher-authored, compact ETL CLI
covering the public behavior of select, filter, map, rename and limit. Visible
development tests cover selected checkpoint-1/2 cases. The checkpoint-3
branch requirement and confirmation tests live in the examiner cache and are
revealed only for the transfer episode. The pinned public repository and
runner remain preserved separately at the revisions in `sources/README.md`.
No official benchmark score is claimed.

Development feedback is explicit: the agent may read its current source,
search ordinary history, run the visible test suite, and run a supplied JSON
probe. The evaluator never returns hidden-test details to the participant.
Teacher trajectories are researcher-authored and executed through the same
tools; teacher construction, validation and unknown labor are recorded.

## Conditions

The first comparison uses the same checkpoint-2 source snapshot and eligible
history for each condition after the acquisition cases:

* ordinary continuation: fresh base-model conversation;
* learned investigation: the same base plus a LoRA adapter trained on the
  earlier tool-use trajectories.

Both conditions have the same source, visible tests, ordinary history and
current task. Each episode loads a fresh model and starts a fresh transcript.
Provider conversation state and generation caches do not cross episodes.

The adapter uses the pinned local MLX Qwen3-4B-Instruct-2507 4-bit checkpoint,
rank-8 LoRA on query/value projections in the final eight transformer blocks,
greedy decoding, and assistant-action-only supervision. The initial pilot uses
four executed teacher trajectories, two per acquisition checkpoint, with no
checkpoint selection or hyperparameter sweep. A later extra-resource arm is
deferred until the procedure is shown to acquire useful behavior.

## Outcomes and stopping

Primary outcome is complete transfer behavior: hidden checkpoint-3 tests pass
and all visible checkpoint-1/2 tests remain passing. Secondary observations
include tool sequence, targeted-test use, patch failures, turns, tokens,
elapsed time, adapter training cost, and reset/load invariants. Failed
acquisition and infrastructure failures are preserved. New seeds on one
history are not treated as independent histories.

Stop after a functioning acquisition regime, an explained acquisition limit,
or a concrete resource constraint. Do not tune on transfer outcomes.
