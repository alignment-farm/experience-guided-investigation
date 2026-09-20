# Experience-guided investigation

An independent Construct-2 ancillary study, commissioned 20 September 2026.

> Can learning from an agent's earlier attempts and failures improve how it
> investigates and completes a later unfamiliar change, after a fresh session,
> when competent access to the same program and source experience remains available?

The initial model-side target is an acquired investigation procedure: use a
current failure or requirement to find relevant earlier evidence, inspect the
affected code, choose a discriminating test, and use its result to repair the
program. Begin with a trainable tool-using model and a retained LoRA adapter for
that behavior. Choose the model and learning method through bounded development;
the starting target is concrete, not a commitment to one optimizer or model size.
Training only final patches or answers would not directly teach this procedure.

**Status:** preparation only. No participant acquisition, training or experimental
result is established. The investigator owns feasibility, workload development,
methods, protocols, execution, diagnosis and publication. Read [AGENTS.md](AGENTS.md),
the [source guide](sources/README.md) and the [starting instruction](PROMPT.md).

## Why this question

Construct studies show useful acquired behavior, but have not established useful
continuing learning across realistic changes against competent alternatives.
In the preceding SQL consolidation study, a developed adapter shortened familiar
execution but completed 6/20 fresh jobs versus 7/20 with external reuse. Teaching
contained only submit/finish actions; fresh adapter runs did not search history
or execute saved queries. That observation does not identify the cause of failed
transfer. This study supplies opportunities to learn the investigation behavior
it will later assess. Prior study failures are background, not participant memory.

Software maintenance is the first test setting for the enduring question of how
agents accumulate useful experience across sessions and where it should live.
Code, tests, notes, searchable history and weights can all retain experience.
Establish acquisition, transfer and useful complete behavior first; then assess
their costs and when the investment pays back. Neither a neural win nor a cheap
solution is required for an informative result.

## Starting workload

Use the pinned SlopCodeBench ETL sequence as the first feasibility lead:

1. Acquire checkpoint 1 validation/normalization and checkpoint 2 linear pipeline
   execution, with explicit development feedback and preserved attempts.
2. Use checkpoint 3 branching/nested pipelines for bounded diagnosis of acquisition
   and later use. Material used to choose the treatment is development material.
3. Freeze the developed treatment before a subsequent change such as checkpoint 4
   named sub-pipelines, parameters and recursion rejection. Keep its requirements
   and confirmation evidence out of participant acquisition and treatment selection.

This is a starting sequence, not a frozen protocol. Root inspected requirements
and ran published reference implementations; it did not run a learner. Code search
is a second lead if competence is feasible, progressing from exact/regex search
to structure-aware matching and file edits. Small motivated variations or a
different workload are allowed when they resolve a material limitation. A later
checkpoint is a new change, not a new independent acquisition history.

Decide what development feedback participants receive before collection. Keep
examiner solutions, future requirements and confirmation tests outside participant
tools and archives. An investigator can inspect public assets without feeding
them to the learner. Preserve benchmark canaries and report changes to feedback
or scoring rather than claiming an official benchmark result.

## Cross-session state

Start a fresh model conversation and reset ephemeral runtime state between task
episodes. Inventory exactly what survives: workspace, tests, ordinary notes,
eligible prompts/tool results/feedback, and the learned state allowed by each
condition. Provider conversation state and inference caches must not secretly
carry experience across resets; record what is retained or cleared. Isolate
condition workspaces and verify base/adapter loading and resets.

All conditions can inspect their program, tests, ordinary notes and searchable
source experience with ordinary tools. Use visible transcripts, not unavailable
private reasoning. Added consolidation sees only eligible past experience and
finishes before the next requirement is revealed. This distinguishes acquired
cross-session behavior from continuing a long conversation.

## Initial contrasts

| Condition | Retained contribution beyond the common acquired workspace/history |
|---|---|
| Ordinary continuation | Ordinary artifact and archive reuse; no additional between-session learning |
| Learned investigation | Adapter acquired from eligible prior attempts, feedback and compatible investigation trajectories |
| Ordinary continuation with extra allowance | Extra current-task inspection, testing or repair comparable to the learning investment |

The last condition tests an alternative use of resources. It spends later, with
the new requirement available, so it is not a pure mechanism ablation. Select a
meaningful allowance, allow unused budget, and report actual native costs; equal
token ceilings do not equate training and inference. Expand this comparison only
after there is a behavior worth interpreting. A source-linked prose aid can be a
useful comparator or diagnosis, but its success is not a prerequisite for neural
development. Disclose teacher work and check that teaching is executable by the
learner's model and tools.

First compare treatments from the same acquired checkpoint-2 workspace and
eligible history. Keep code, tests and ordinary notes matched to isolate the
additional contribution. If consolidation changes those artifacts, report that
as a distinct intervention. A later continuing comparison can let each policy
accumulate its own work products, failures and learning; it answers the broader
question of policy value. Do not remove useful code, caching or source access to
create an artificial advantage for memory. Record differences in delivery as
well as representation when one treatment supplies material directly.

## Prospective expectations

CC1–CC3 are copied unchanged from root's 20 September brief. Append assessments
without rewriting them. They are predictions, not results.

- **CC1 — Residual experience value.** Added processing will be most useful when
  earlier work established a consequential reason, diagnostic or limitation that
  is difficult to recover from the current code and ordinary archive in time.
  Rephrasing an already explicit contract should add little. Compare complete
  later behavior and retrieval/repair effort, and inspect which source evidence
  explains any difference.
- **CC2 — Opportunity cost.** Some gains over ordinary continuation will disappear
  when it receives comparable extra resources for current-task inspection and
  testing. Advance consolidation should have a stronger case when its acquired
  contribution serves several later changes; repayment over that horizon remains
  to be demonstrated rather than assumed from one faster response.
- **CC3 — Artifact mediation.** In these short software sequences, part of any
  continuing-policy advantage will reside in better code and tests. An advantage
  with policy-specific workspaces need not survive a matched-workspace diagnostic.
  If it does survive, identify the additional retained contribution rather than
  attributing the whole sequence gain to it.

## Evidence and stopping

Verify mutable-state access, then demonstrate acquisition of the target behavior
on development cases. Finite gradients, a changed adapter and reduced loss do not
establish successful acquisition. Preserve failed runs and use bounded diagnostic
comparisons to distinguish teaching, model, tool-interface and optimization
limitations when warranted. A model/harness change can establish a functioning
regime; distinguish that capability improvement from the effect of experience.

Evaluate complete new behavior and still-valid earlier obligations together.
Superseded requirements are not forgotten obligations. Use submitted snapshots,
separate infrastructure from task failure, and inspect meaningful behavioral
checks rather than treating test counts or fewer tool calls as complete success.
Confirm claims developed through diagnosis on fresh material. New seeds on one
history do not establish independent-history generality.

Account for acquisition, teaching, failed training, source processing, delivered
context, inference, retrieval, validation, tests and repair. Distinguish shared
acquisition, research development and deployment costs; preserve unknowns and
native units. Cost qualifies the value of demonstrated behavior, not whether a
learner deserves development. Several later uses may be needed to assess repayment.

Publish a concise README abstract linked to evidence, reproduction instructions
and revision identifiers. Explain what worked, what failed and which explanation
the evidence changes. Completing a publication does not end the commission:
continue a useful bounded next step within the remit. Stop on explanatory progress,
a demonstrated limitation or a concrete resource constraint, with a brief reason.
Neither one failed recipe nor an indefinite search for a winning recipe is enough.

Construct Runtime is an optional instrument. No new general harness is required.
Keep implementation and evidence here; root retains theory, synthesis and
independent research questions while this study runs.
