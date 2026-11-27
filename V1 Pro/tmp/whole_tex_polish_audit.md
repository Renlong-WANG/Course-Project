# Whole-manuscript editorial audit

Scope: polish existing English text, reduce equation numbering, and improve the structure of Section 4. Retain the finite-aggregation/Lagrangian-duality/max-flow proof route, all substantive mathematical statements, citations, theta=0, and existing comment archives. Keep Xi, X_i, Xi_j, N^{te}, bold vectors, and explicit joint-measure differentials. No appendix or subsections.

## Findings and proposed edits

- Numbering: auxiliary definitions, Lagrangian algebra, pointwise envelope formulas, endpoint moves, and column allocations are all numbered. Retain numbers for the main model, DW and calibration results, finite rank constraints, measure and dual programs, strong-duality relation, essential finite primal formulations, and closed-form bounds. Replace references to unnumbered algebra with the relevant mathematical object or theorem.
- Section 4, input cells: restore a coherent definition of input cells and their probabilities; remove the stray trailing K from w_i. The intended probability is the difference of the two surrogate CDF values.
- Section 4, post-lemma transition: remove the dangling reference to eq-input-cells; use the already-defined input cells directly. Keep residual cells, cell penalty values, and failure coefficients in that order.
- Sections 2--3: tighten repeated setup and long sentences. Preserve the training/test sampling assumptions and all coverage statements. Present the failure-probability coverage proof directly for the DW set; retain the generalization in the discussion.
- Section 4: replace procedural announcements and rhetorical exactness questions with a concise mathematical progression. Preserve the constructive endpoint argument and explain its feasibility at coincident thresholds.
- Section 4, proof organization: distinguish finite probability allocation, realization by joint laws, finite-LP duality, and lifting dual solutions to marginal functions through paragraph structure. Keep all technical steps in the main text.
- Closed forms: retain the nested-cut max-flow proof and explicit upper/lower column allocations. Remove labels and numbers from these intermediate formulas. Connect the resulting extrema to the numbered finite primal representation and final bounds.
- Style: remove filler such as “Notably,” repeated “we first ... then ...” announcements, and unnecessary negative framing. Keep qualifications that carry sampling, support, or numerical-confidence conditions.

## Evidence and preservation

The manuscript contains theoretical statements, not empirical performance claims. No new experiments, comparisons, citations, confidence levels, or mathematical results will be added. The correction of the stray K is the sole intended numerical/algebraic correction. The pre-edit source, PDF, and bibliography are backed up in backups/whole_tex_polish_20261124_212156.
