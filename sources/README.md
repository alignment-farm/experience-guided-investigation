# Starting sources and inspection boundaries

Prepared 20 September 2026 from Construct-2's reading and task-asset inspection.
These are starting sources, not a claim that this study reproduced public results.
Root's records are copied in [root-preparation](root-preparation/provenance.json)
with their origin paths and hashes. Paths inside those reports describe the root
host; they are not this study's experiment outputs or guaranteed local assets.

## First workload: inspected runnable reference assets

- SlopCodeBench, **P96 `2603.24755v2`**:
  [exact paper](https://arxiv.org/html/2603.24755v2).
  The published setup carries code across checkpoints with conversation resets;
  official grading feedback is withheld. Declare any local feedback adaptation.
- [Problem repository](https://github.com/gabeorlanski/scb-problems/tree/ef6a9dd13911566b6b01075ca121758c9f7b5c5f),
  pin `ef6a9dd13911566b6b01075ca121758c9f7b5c5f`, Apache-2.0.
  Root inspected `etl_pipeline` and `code_search` checkpoint 1–4 specifications,
  test interfaces, selected assertions and reference entry points/dependencies.
  ETL checkpoint 5 was only surveyed.
- [Runner](https://github.com/SprocketLab/slop-code-bench/tree/c2a53b46ed7227545951168e1dfeea8a6eec9316),
  pin `c2a53b46ed7227545951168e1dfeea8a6eec9316`, MIT.
  Root inspected documentation, prompts, reset and prior-test selection code;
  it did not install or run the full runner. The May problem and September runner
  pins are inspection boundaries, not a reproduction of the paper environment.

Root directly executed published references: ETL checkpoint 3 passed 117/117
tests from checkpoints 1–3; checkpoint 4 passed 134/134 from 1–4. Code search
passed 47/47 and 75/75 respectively. These 373 executions overlap and are not
373 independent tasks. They establish reference feasibility, not participant
acquisition, feedback suitability or memory value. The copied
[reference checks](root-preparation/reference-checks.json) and
[asset manifest](root-preparation/artifact-manifest.json) preserve pins and hashes.
Clone owned assets under an ignored directory before local execution; keep
examiner references and future tests outside participant tool access.

## Methods that answer, narrow or redirect this study

| Exact primary text | Inspected implication and boundary |
|---|---|
| AgentCL, **P88 `2606.02461v2`**, [paper](https://arxiv.org/html/2606.02461v2) | First-pass, repeated and held-out work are distinct outcomes. Nonparametric experience learning is prior art; published results do not answer this model-side comparison. |
| AgentOdyssey, **P87 `2606.24893v1`**, [paper](https://arxiv.org/html/2606.24893v1) | Weights plus explicit memory are an existing direction, not this project's architectural novelty. |
| Co-Evolving Harnesses and Models, **P42 `2609.09134v1`**, [paper](https://arxiv.org/html/2609.09134v1) | Learner rollouts and compatible corrected teaching offer acquisition methods. Author results are not a diagnosis of Construct's failures. |
| HarnessForge, **P89 `2606.01779v1`**, [paper](https://arxiv.org/html/2606.01779v1) | Model/harness compatibility is a method to inspect when teaching fails, not a mandatory recipe. |
| SWE-Milestone, **P98 `2603.13428v4`**, [paper](https://arxiv.org/html/2603.13428v4) | Real-history extension: 98 milestones in seven repositories. The independent baseline resets canonical code; that does not isolate memory at a shared acquired workspace. Root inspected only implementation docs, not runnable instances. |
| SWE-Bench-CL, **P99 `2507.00014v1`**, [paper](https://arxiv.org/html/2507.00014v1) | Resets each issue to its base commit. Preliminary evaluation limitations and proposed comparisons narrow claims; these are not positive continual-learning evidence. |
| Measure Before You Manage, **P100 `2608.31057v1`**, [paper](https://arxiv.org/html/2608.31057v1) | Actual context, auxiliary work and incomplete runs matter. Repeated calls alone do not establish successful repair; use complete behavior and actual costs. |

SWE-Milestone docs were read at
[`17a8f1593e172e26b36cea15e2b30fb9536c93f5`](https://github.com/DeepCommit-ai/SWE-Milestone/tree/17a8f1593e172e26b36cea15e2b30fb9536c93f5):
README, setup guide and benchmark-version file (`v1.0.2`). Dataset instances and
image digests were not verified. This is a later lead; a large benchmark download
is unnecessary for the first pilot.

CL-Bench database drift, **P90 `2606.05661v1`**, remains a reserve. Root rechecked
code at `5f8c50eb1e84b2eda2ef4faff757dfc812a0ea26` and dataset revision
`a0cc57eeb9a54f01c0490a1b46cb705b4e05aa19`. Five reference queries reproduced,
but the numeric grader accepted two of three selected stale-column diagnostics.
Those observations do not establish a global error rate or correct reusable SQL.
Earlier local normalization and exposure also limit its value as a new history.

## Local antecedents and optional instrument

- [Weight-consolidation publication](https://github.com/alignment-farm/weight-consolidation/tree/80c17db):
  root accepted the bounded continuing-SQL phase at `80c17db`. It motivates
  teaching investigation behavior but does not establish why transfer failed.
- [Construct Runtime](https://github.com/alignment-farm/construct-runtime/tree/09f66837ca76db1f674ee3372d734219ad0f3e27):
  optional instrument, last root review at `09f66837ca76db1f674ee3372d734219ad0f3e27`.
  Its memory-worker demonstration improved 9/28 to 26/28; cheap retrieval reached
  28/28 and identifier/order sensitivity limited the learned result. The build
  supplies separable execution/learning and MLX paths, not demonstrated useful
  continuing memory. Inspect instructions and pin an owned copy if used. Do not
  edit the derivative's active checkout or assume a later revision was reviewed.

For the full root reading boundaries, see Construct-2's
`sources/2026-09-20-task-sequences/README.md`,
`sources/2026-09-20-experience-comparison/README.md`,
`sources/2026-09-20-continuing-capability/README.md` and
`sources/2026-09-17-runtime-study-selection/README.md`. They are contextual
reading, not required orchestration. Record this study's own discoveries and
inspection depth as its question develops.
