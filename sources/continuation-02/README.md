# Focused method inspection, 28 September 2026

Question: can strict parsing/usable feedback repair this pilot's interface, and
how can actual failures supply compatible training targets?

Inspected [SWE-agent 2405.15793v3](https://arxiv.org/html/2405.15793v3), §§2–3:
small action spaces, compact actions, bounded file windows and informative
feedback motivate this continuation's shared tools. These are established methods,
not a claimed invention or a reproduction of author benchmark scores.

Inspected [Co-Evolving Harnesses and Models 2609.09134v1](https://arxiv.org/html/2609.09134v1), §3.4:
correcting a failing turn in a learner rollout is a concrete alternative to
whole expert-trajectory imitation. The author-reported improvement does not
establish what this ETL learner will acquire. A local correction branch, if used,
will be explicitly distinguished from their full pipeline.

Exact-version metadata was retrieved in one arXiv API request with User-Agent
`experience-guided-investigation/0.2 (bounded interface and acquisition methods study)`;
response and headers are cached here. A preceding sandbox DNS failure sent no
successful request. No parallel API/OAI client was used. Primary HTML was
inspected through the web tool; root's local review was read as secondary context.
