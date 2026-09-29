# Autonomous action and feedback use — continuation 03

Development continuation of the existing ETL history, 28 September 2026. Starting revision `523eb3fb8aa56fed0ffdfe10f6b1f1cb3002ade6`. The bounded phase is complete: 15 participant episodes, two executed correction continuations, and a fixed 46-update saved adapter (plus one recorded discarded update).

Competent ordinary reuse completes the joint repair; the new LoRA does not demonstrate autonomous acquisition. The resident 27B reference reproduces both defects, repairs and verifies them, runs the public suite, and passes 18 original checks plus ten fresh contract cases. Ordinary 4B repairs only filter; learned 4B remains in a read loop. No unfamiliar-change transfer was evaluated.

The user selected reliable autonomous action and feedback use with competent ordinary reuse as comparison. Native function calls, executable retained checks, copyable source, and direct reuse of past programs were developed before the new neural treatment. Interface changes are shared infrastructure, not a learned-weight effect. Historical and current verification are explicitly distinguished. No hidden automatic repair or completion gate exists.

Evidence inventory:

- `runs/`: full raw model/tool records, submitted programs, episode summaries, interruption records. Every interrupted maintenance pilot counts toward the 16-episode budget.
- `evaluation.json`: unchanged external development obligations, 18 checks plus six public tests. These score submitted behavior, not the entire investigation procedure.
- `action-audit.json`: actual actions, assertions, public-suite calls, malformed replies, tokens and elapsed time.
- `history/`, `reuse-history/`, `complete-history/`: successive ordinary-access archives; manifests inventory every retained file. Failed attempts and full teaching records are preserved. No future requirement/examiner implementation is exposed in these archives.
- `acquisition/`: executed continuations of actual learner attempts, target rows and lineage. Fifteen learner actions plus eight investigator correction actions; three defective edit targets masked, their feedback/context retained. Development invalid-type feedback explicitly promoted into teaching.
- `adapter-cached-v2/`: fixed 46-update native-tool LoRA, manifest and raw optimization record; `adapter/` and `adapter-cached/` preserve failed attempts. Updates alone do not establish acquisition.
- Harness validations: `harness-validation.json`, `native-template-checks.json`, `native-tool-validation.json`, `replay-validation.json`.
- Model/runtime pins: `environment.json`, `coder-model-manifest.json`, `served-model-inspect.json`; method discovery in `../../sources/autonomy-03/README.md`.

The protocol was accidentally overwritten during preparation. The overwritten content is saved as `protocol-accidental-overwrite.py`, and `../../protocol/autonomy-v3.md` was reconstructed from the session record before neural training. It must not be represented as an intact preregistration.

Requested investigator: OpenAI gpt-6-astra; actual backend identity and reasoning setting were not exposed. Local MLX and the provided Docker Model Runner endpoint supplied participants. The endpoint is the same Mac Studio as this checkout; a sibling study shares its resident model. Its processes and files were not modified. Own heavy jobs are serialized. Timing is confounded by shared load; investigator and teacher costs are unknown. No newly purchased participant API calls.

Participants: `mlx-community/Qwen3-4B-Instruct-2507-4bit` is the learner and matched ordinary base; `mlx-community/Qwen2.5-Coder-7B-Instruct-4bit` was a development alternative. The served reference requested `docker.io/ai/qwen3.8:27b-q4_K_M`, with its observed content ID and response model paths retained in `served-model-inspect.json` and raw events. No unobserved backend identity is inferred. Runtime: MLX 0.32.2, pinned mlx-lm 0.32.0, Transformers 5.17.0; Docker client/engine 29.8.0, Model Runner client v1.2.6/server v1.2.8. Exact revisions and hashes are in the manifests.

Earlier phase evidence and CC1–CC3 are preserved. This is neither an official benchmark score nor an independent sample of histories.

Retained-check provenance matters: the filter check comes from the previously executed strict-filter correction; rename_trim and limit_zero reuse original executed teacher outputs. No check was synthesized from the future reject suite. The learner still decides whether to run, adapt, or ignore each check. The ordinary reference may restore an entire historical program, then verify current behavior.

The joint acquisition workspace combines the already exposed non-None filter defect with the learner's own `.strip()` rename-validation defect. Its requirement explicitly asks for both obligations and current regression verification. This is a development recombination, not fresh transfer. Supplying the complete current source and history index is a shared scaffold, and all ordinary arms retain those affordances.

## Ordinary development results

| Interface/model | Filter checks | Rename checks | Procedure observation |
|---|---:|---:|---|
| Manual JSON, 4B | 9/18 | 16/18 | Read then stopped; unrelated/non-discriminating probe |
| Manual JSON, 7B coder | 9/18 | 16/18 | Historical source not applied; repeated failed edits |
| Native tools, 4B before casebook | 13/18 | — | Failure→edit→retest and public suite, but truthiness violates boolean-only contract |
| Native tools + casebook, 4B | 18/18 | 17/18 | Filter recovered from a wrong edit using a failed mixed-type probe; neither episode ran public suite; rename missed invalid-type preservation |
| Native tools + casebook, resident 27B | 18/18 | 18/18 | Both repaired and verified current behavior; public suite executed in both |

All scores use the same 18 obligations. The external six-test public suite additionally passes for both final 27B programs and the final 4B filter program. External test execution is not credited as participant work. Three other pilots were interrupted (two interface defects, one repeated non-tool output); all raw failures count. Interface and model changes occurred during development, so the table is diagnostic, not a randomized causal ablation. The two 27B episodes demonstrate competence here, not a general reliability rate.

The 27B rename episode also made a malformed semantic probe with mismatched whitespace, observed its failure, and corrected the input/expectation. The failed probe remains in the record; a final correct program does not erase intermediate mistakes.

## Resource-driven training revision

The original full-prefix gradient attempt reported 19.92 GB peak after one recorded update despite a requested 12 GiB allocator limit. It was interrupted; no adapter was saved. Its raw log, trainer snapshot and intervention are retained in `adapter/`. An initial cached-prefix validation then stopped before updates on a one-ULP bfloat16 loss discrepancy; its elapsed field also has a documented variable-shadowing defect (`adapter-cached/`). These are implementation failures, not negative acquisition results.

The revised `autonomy_train_cached.py` recomputes every prefix token at current weights in 512-token chunks, detaches prefix KV, and backpropagates through action-token suffixes only. It neither truncates text nor reuses stale cross-example cache. This deliberately omits prefix-state gradients and must not be described as ordinary full-context SFT. Native action templates, 23 targets, two epochs, seed 17, rank 8 final-eight-layer Q/V LoRA, AdamW 5e-5 and fixed checkpoint selection remain unchanged. Small/full-row forward losses are checked within declared bfloat16 tolerance before training; measured memory is checked after each update. All attempts count toward resource reporting.

## Reproduction and storage

Use a disposable checkout and the pinned model artifacts (read-only paths are recorded in environment/manifests). `uv sync --extra adaptation` installs the pinned environment; run scripts with `UV_CACHE_DIR=/tmp/egi-uv-cache uv run --no-sync python`. Metal requires access outside the restricted shell sandbox. Do not overwrite the published run directories; both inference and training refuse existing output paths.

Identical workspace history copies are excluded from Git. `workspace-history-manifests.json` records every path/hash and a retained content object. Run `scripts/autonomy_restore_histories.py` to reconstruct or verify them exactly; it refuses to overwrite changed files. Earlier histories, full failures and corrections remain intact in the shared archives.

To replay a specific saved episode, restore its initial source from the recorded task variant (joint construction in `autonomy_joint.py`), copy its manifest-matched history into a fresh workspace, and use `autonomy_tool_agent.py --model MODEL --workspace WORKSPACE --output NEW_OUTPUT --max-turns 20`, with the selected `--adapter` only for learned runs. The original initial messages and tool schemas are recorded in each run's provenance event. Early interface versions are preserved separately and must not be silently replaced when reproducing early results. Serving reproduction additionally requires the exact resident model and an accessible endpoint; server cache/load state was not isolated.

Native teacher derivation is replayable with `autonomy_acquire.py` in a disposable output tree containing the saved ordinary attempts and reuse history. Train with `autonomy_train_cached.py --model MODEL --training evidence/autonomy-03/acquisition/training.jsonl --output NEW_OUTPUT --epochs 2 --seed 17`. The failed full-gradient attempts are diagnostic history, not required predecessors for the saved learned adapter.

## Joint development contrast

The combined task starts with the already taught non-None filter bug and the learner-generated `.strip()` rename type-validation bug. Both 4B arms get byte-identical current source/task/full history, native tools, temperature/seed and the same 12-action diagnostic budget.

| Arm | Original checks | Fresh contract cases | Actual procedure |
|---|---:|---:|---|
| 46-update learned 4B | 8/18 | 3/10 | One history search and 11 reads; no current probe, edit, public test or completion |
| Ordinary 4B | 17/18 | 5/10 | Failed mixed-type probe→correct filter edit→passed probe; trim probe and public suite pass, but invalid-type rename remains broken; completion overstates repair |
| Ordinary 27B reference | 18/18 | 10/10 | Both defects reproduced, both repaired and verified; public suite passes; truthful completion in 19 actions under a separate 20-action cap |

The learner initially had a 20-action cap. After 11 search/read actions and repeated unchanged transcript reads, the diagnostic was adaptively limited to the first 12 actions; the ordinary control was capped at 12 before running and completed in 11. The learner was interrupted while beginning another unexecuted inference. This is a development cutoff, not proof of failure after 20 actions or eventual inability. The raw prefix, intervention and partial-work timing are retained. No checkpoint, teaching, model or tool change followed these outcomes.

The ten additional contract cases were frozen before joint outcomes and never supplied to participants or teaching. They confirm that the ordinary 4B rename defect is broader than the single original invalid-source check. They are fresh input material within this history, not unfamiliar-change transfer. The old 18-check scores remain unchanged. The learned arm fails the prospective acquisition gate, so the previously authored reject extension remains untested.

Both corrected separate-task 27B reference submissions also pass all ten new confirmation cases. Its same-joint run also passes the acquisition procedure checks. The larger reference has a 20-action budget, compared with the adaptively chosen 12-action 4B diagnostic budget; this is not a matched cross-model efficiency comparison. See `joint-acquisition-ordinary27-evaluation.json` and its raw run.

## Boundaries

Direct read/search/restore paths are restricted to each workspace; future requirements and examiner code are absent from all participant prompts and histories. Python test/probe subprocesses were not independently OS-jailed. The full edits and submitted-code import/call inventory show no observed introduction of external I/O; this is an access audit, not an adversarial isolation proof. A future hardened runner should restrict subprocess filesystem/network access too.

MLX maintenance calls rebuild the supplied conversation prefix at each turn; there is no cross-turn prompt-cache reuse in this implementation. Server responses separately report cached prompt tokens. Therefore wall-time/token accounting does not establish efficient resource repayment, and repeated reads amplify the MLX implementation's timing cost. Episode reset still uses a new process/model/conversation, and no KV state is deliberately retained between episodes. Historical code and test reuse are explicit and available to every matched arm.

The paired-prefix audit locates the first observed divergence: initial messages, source, tool schemas and whole eligible histories match. Both 4B arms issue the same first two actions and receive identical results, with the same generated-token counts. At action 3, the learned arm chooses an older teacher transcript; the ordinary arm chooses the recent correction record and later proceeds to current execution. This supports a focused action-selection diagnosis. It does not identify a unique training mechanism or establish a general harmful effect of LoRA.


## State checks, costs and stopping decision

`isolation.json` verifies that loaded adapter parameters match the saved hash, frozen base parameters are unchanged, the initial zero-adapter state is restored, and actual observed generations return after restoration. The adapter changes an observed output, but that fact is not acquisition. Each MLX maintenance episode uses a fresh process/model/conversation; inference seed is reset after optional LoRA initialization. Served episodes reset the client conversation and workspace, while server state remains shared. The joint pair also passes whole-history/source/schema parity checks (`paired-prefix-audit.json`).

`costs.json` records about 72.1 minutes of serial heavy-job elapsed work, including serving, failed training and reset checks. This includes a conservative 60-second charge for the failed validation whose timing log is invalid; small preparation/validation costs and investigator/teacher costs are not fully priced. There are 47 recorded completed updates: one discarded full-gradient update and 46 in the saved treatment; another discarded evaluation was interrupted in flight. The saved run took 706.2 seconds, peaked at 5.70 GB and produced a 2,624,893-byte adapter. No newly purchased participant API calls were used. Server load/caching and MLX prefix recomputation prevent an isolated timing or resource-repayment claim. The 16-episode, 64-update and 90-minute ceilings were not exhausted.

This phase closes on explanatory progress and a demonstrated local acquisition limitation. Usable tool syntax, full code/test/history reuse and complete autonomous behavior exist in this instrument. The new treatment's failure is action selection and transition to current verification, not absence of correct historical code or an inability to parse any action. The ordinary 4B false completion also shows why passing a narrow probe/public suite is insufficient for still-valid obligations. No general reliability rate, neural-learning impossibility, model-family ranking or unique training failure mechanism follows; model capacity, target weighting, optimization and stopped-prefix gradients remain competing explanations.

The best next study is a revised acquisition comparison focused on decisions at actual stagnant/false-completion states, or a stronger trainable learner with demonstrated acquisition. It needs new development and confirmation material and a declared matched budget. The remaining single participant episode is not spent on an unpaired checkpoint retry. The unused reject extension remains future material. CC1 is unresolved; CC2 and CC3 are untested. The broader commission is not retired.
