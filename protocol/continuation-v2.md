# Bounded acquisition diagnosis, 28 September 2026

Starting revision: 121242ca597c607f06d9f9084d88b1fa90a458ff.
This is development; no old pilot or reviewer-exposed case is fresh confirmation.
Original pilot outputs, implementation and protocol remain unchanged.

Budget before collection: one local MLX job at a time, at most 90 GPU minutes,
12 maintenance episodes of at most 12 turns and 1024 output tokens per action,
and at most 32 additional LoRA updates. No paid API calls. The local GPU is
available after sandbox escalation; process inspection found no active MLX job.
Remote serving/mutable access are probed separately; no shared Studio training
is planned. Stop expansion on useful explanatory progress or a concrete limit.

First diagnose the existing Qwen3 4B learner and saved pilot adapter on the two
original teaching repairs and the reviewer-exposed boolean-only filter repair.
Use identical, fresh workspaces and full pilot executed teaching records for both
arms, including training prompt/targets, task requirements and original tool
feedback. These records are researcher-authored teaching, not learner experience.
They are directly inspectable with paginated read and searchable history.

Shared interface changes: strict single-object parsing (reject composite output),
1024-token action cap, paginated reads, structured CLI JSON feedback with explicit
application success, optional expected-output assertions on probes. Exact narrow
edits remain available. No hidden checker feedback is returned during an episode.
Record actual edits, probes, suite results and completion declarations separately.
No claim will attribute the bundled shared-interface change to learned weights.

External development evaluation: all six preserved public tests; filter values
true, false, 1, 0, -2, 1.5, strings, null and missing fields, comparisons and error
path; normalization trimming and invalid types; limit zero/positive and invalid
boolean/negative values. Checks are outside participant roots. Passing tests are
bounded evidence, never a proof of every ETL requirement.

If this establishes a usable action regime, collect actual failed participant
attempts and execute identified teacher corrections. Keep raw attempts and all
correction records in ordinary history. Train only on eligible development work;
verify loaded weights and fresh-process acquisition behavior before interpreting
transfer. New work must be specified and frozen before its evaluation and not
used to select treatment. Extra-resource comparison follows useful behavior.

Inventory: each process loads base and optional saved LoRA anew. Conversations,
KV caches and runtime objects do not persist. Only explicit source/tests/history
and declared adapter survive; filesystem/model caches remain competent. Fresh
workspaces isolate edits. Model files are read-only sibling assets pinned by the
pilot manifest; no sibling is modified. Investigator requested policy is OpenAI
`gpt-6-astra`; backend identity and actual reasoning setting are not exposed by
this session, so they are not inferred. Codex CLI reports 0.158.0; MLX 0.32.2,
mlx-lm 0.32.0, transformers 5.17.0. Investigator/teacher token cost is unknown.

## Adaptive correction decision (after first filter evaluations)

Base failed to act; the pilot adapter made the same truthy-filter repair despite
the shared boolean warning. The executed correction preserves adapter turns 0–2
and replaces its premature turn-3 edit with a mixed-type probe, strict repair,
repeat probe, public suite and done. Two successful learner prefix actions and
five investigator continuation actions form seven supervised rows. This is a
learner-grounded correction branch, not single-turn-only method reproduction.
Initialize a NEW LoRA from base (prefix policy was old adapter; cross-policy
teaching is disclosed), rank 8, final eight Q/V layers, four epochs = 28 updates,
AdamW 0.0003, seed 17 for Python and MLX. No checkpoint selection. Test complete
filter reacquisition before any transfer interpretation. Preserve both original
failures and executed corrections in all later arms' searchable history.

## Conditional-context diagnosis

Fresh-reset correction-adapter acquisition enters a repeated-read loop instead
of the corrected branch. Before interpreting transfer, test both base and new
adapter from the exact three-turn prefix on which the executed correction begins.
Replay prefix reads and rejected malformed action, inject those declared three
turns, then let each model act freely. This is coached, conditional development
acquisition, not fresh-session autonomous acquisition or transfer. It separates
learning a response in a taught context from reaching and using it autonomously.
No further optimization or checkpoint selection is permitted. A subsequent
authored reject task has been frozen but remains unevaluated until acquisition
status justifies its use; preparation is not confirmation.

## Final bounded bridge intervention (before its outcomes)

Conditional prefix replay produces a strict edit but no discriminating probe; the
fresh-reset learner loops on reads. Allocate the last four updates of the 32-step
budget to the actual fresh-reset correction-adapter turn-2 context: replace that
read with the already executed mixed-type probe. Execute the target in the same
source state and preserve its failed assertion. Train one row for four epochs,
initializing from the fixed 28-step adapter, with unchanged optimizer/settings.
This supersedes the earlier no-further-optimization decision for a specified
on-policy context-gap diagnosis; it does not select on fresh material. The last
two maintenance episodes compare base and this bridge adapter with full updated
source history. No extra-resource or transfer claim follows merely from loss.
