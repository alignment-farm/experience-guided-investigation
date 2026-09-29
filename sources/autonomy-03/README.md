# Interface and participant-method inspection — 28 September 2026

The live [Transformers chat-template documentation](https://huggingface.co/docs/transformers/chat_templating)
was inspected for role formatting, generation boundaries and special-token handling.
The local installation is transformers 5.17.0. Its loaded Qwen templates produce
real newline/control-token sequences, not escaped text; a direct tokenizer check
confirmed this for both local candidates. Native message roles are established
usage, not a novel learning method or a proved diagnosis of earlier failures.

The [Qwen3-4B-Instruct-2507 model card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)
and locally pinned converted model card were inspected for model identity. The
shared-tool changes also build on the earlier selected SWE-agent inspection in
../continuation-02/README.md; no new arXiv metadata request was required here.

The candidate Qwen2.5-Coder-7B-Instruct-4bit was checked against the Hugging Face
repository API with blob metadata. All local bytes match repository revision
019cc73c45c770444708a6dd8690c66243cc5c80. Its card has a base_model-field discrepancy
(base name without Instruct), while the title/conversion paragraph identify
Instruct. The full match to that exact upstream repository is the identity claim;
its original training provenance is not independently established. This is model
provenance, not evidence that it will be a competent maintenance participant.

Cached API metadata and the study's candidate model manifest preserve retrieval.
No author benchmark result was reproduced and no fresh ETL requirement was used
for selecting these interface changes.

A focused follow-up inspected the Qwen3 model card's Agentic Use section: it
recommends Qwen-Agent's native tool templates/parsers. We use the already pinned
Qwen chat-template function schema format rather than installing that framework.
Both local tokenizers were directly checked for tools, tool_call and tool_response
markers and the assistant generation prefix. This is compatible-format
implementation, not a reproduction of Qwen-Agent results or proof that format
alone explains our failures. Normal restore-from-history is an ordinary reuse
capability; completion remains externally audited rather than presumed from it.

Memory diagnosis, 28 September: inspected installed mlx-lm 0.32.0 Qwen3 attention, grad_checkpoint and KVCache code, plus official MLX docs for [set_memory_limit](https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.set_memory_limit.html) and [stop_gradient](https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.stop_gradient.html). The requested allocator limit did not bound locally observed peak. A long-prefix backward attention allocation is an inference, not isolated measurement. Local replacement recomputes full prefix state each update but stops its gradient; it changes the gradient estimator, not the available conditioning tokens. Search also surfaced IonDen/mlx-train-perf as a discovery lead; no code or results from it were adopted or independently verified. No arXiv request was made.

Follow-up inspection of the official set_memory_limit page (documentation banner0.32.3; local runtime0.32.2) clarifies that the limit is a graph-evaluation guideline; allocations may continue beyond it when memory/swap is available. This supports the observed overshoot and corrects the initial assumption that the setting was a hard cap. Local measured checks remain necessary. Official stop_gradient documentation specifies an unchanged forward value with gradient flow blocked; the prefix-gradient omission is therefore intentional and disclosed.
