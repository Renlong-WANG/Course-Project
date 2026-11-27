from datetime import datetime
from pathlib import Path
import collections
import json
import re
import shutil

root = Path.cwd()
path = root / 'manuscript.tex'
original_bytes = path.read_bytes()
original = original_bytes.decode('utf-8').replace('\r\n', '\n')
body_start = original.index(r'\section{Problem Description}')
body_end = original.index('% BEGIN OPTIONAL APPENDIX:', body_start)
old_body = original[body_start:body_end]
body = old_body
edits = []

def replace(old, new, purpose):
    global body
    assert body.count(old) == 1, (purpose, body.count(old))
    body = body.replace(old, new, 1)
    edits.append({'purpose': purpose, 'before': old, 'after': new})

replace('The following definition uses the corrected discrepancy to constrain the residual CDF simultaneously over all thresholds.',
        'We use this discrepancy to define the residual ambiguity set.', 'definition lead')
replace(r'In Definition~\ref{definition-dw-ambiguity-set}, $\theta$ controls the allowed corrected likelihood discrepancy. The induced CDF tolerances vary across probability levels and can be asymmetric about the empirical CDF. Calibrating $\theta$ assigns a confidence level to this simultaneous band.',
        r'The induced CDF tolerances vary by probability level and can be asymmetric. Calibration links $\theta$ to a confidence level.', 'definition interpretation')
replace(r'The following proposition calibrates $\theta$ using the uniform reference statistic and establishes conditional coverage of the true residual law.',
        'The uniform reference law yields a distribution-free calibration.', 'calibration lead')
replace(r'Proposition~\ref{proposition-01} applies to arbitrary residual distributions, including laws with atoms or infinite moments. For fixed $\phi$ and $\psi$, the reference law depends only on $N^{\mathrm{te}}$, so $\theta_{N^{\mathrm{te}}}(\delta)$ can be calibrated offline. \citet{L.J23} describe finite-sample evaluation using uniform order-statistic boundary probabilities. A conservative upper bound on the quantile in \eqref{eq-dw-calibrated-threshold} preserves \eqref{eq-cdf-coverage}.',
        r'The guarantee allows atoms and infinite moments. For fixed $\phi$ and $\psi$, the reference law depends only on $N^{\mathrm{te}}$, so thresholds can be precomputed. \citet{L.J23} give finite-sample evaluation through uniform order-statistic boundary probabilities. A conservative quantile upper bound preserves \eqref{eq-cdf-coverage}.', 'calibration interpretation')
replace(r'The following theorem transfers the residual-law coverage in Proposition~\ref{proposition-01} to the upper and lower failure probability bounds.',
        'Residual-law coverage also controls the failure probability interval.', 'failure-coverage lead')
replace(r'Theorem~\ref{theorem-01} uses the same residual-coverage event for both endpoints, so $1-\delta$ is the confidence level for the entire interval. For fixed test data, $0\le\theta_1\le\theta_2$ implies $\mathcal Q^{\mathrm{DW}}(\theta_1)\subseteq\mathcal Q^{\mathrm{DW}}(\theta_2)$, making the lower bound nonincreasing and the upper bound nondecreasing in $\theta$. A higher prescribed confidence level requires a nondecreasing calibrated threshold and therefore gives a wider or unchanged interval.',
        r'For fixed test data, $0\le\theta_1\le\theta_2$ implies $\mathcal Q^{\mathrm{DW}}(\theta_1)\subseteq\mathcal Q^{\mathrm{DW}}(\theta_2)$. The lower bound is nonincreasing and the upper bound nondecreasing in $\theta$, so higher confidence gives a wider or unchanged interval.', 'failure-coverage interpretation')
replace('The following corollary extends this common coverage event to all response thresholds using the same calibrated ambiguity set.',
        'The same coverage event can be used across response thresholds.', 'threshold-coverage lead')
replace(r'Corollary~\ref{cor-simultaneous-threshold-bounds} gives the entire response-threshold curve from one residual calibration, including thresholds selected after observing the test data, with a common confidence level across $c$. Complementing the endpoints also bounds the strict exceedance probabilities $\Pr \left\{g(\bm X)>c\right\}$ simultaneously. Here $g$, $\hat g$, and the input law $\mathbb P$ remain fixed. Fragility curves formed by conditioning on different hazard intensities require coverage for the corresponding conditional residual laws.',
        r'Thresholds may therefore be selected after observing the test data. Complementing the endpoints gives simultaneous bounds on $\Pr \left\{g(\bm X)>c\right\}$. The functions $g$, $\hat g$, and the law $\mathbb P$ remain fixed; hazard-conditioned fragility curves require coverage for the corresponding conditional residual laws.', 'threshold-coverage interpretation')

replace(r'Throughout this section, the training data, the test residuals, and $\theta\ge0$ are fixed. We use the observed residuals to partition both the residual and input spaces. These partitions express the DW restrictions as cumulative cell probabilities and reduce the Lagrangian duals to finite linear programs. A joint-distribution construction establishes exact finite primal representations, after which LP duality and the ordering of the cells yield strong duality and closed-form bounds. The main development takes $\Xi=\mathbb R$; Remark~\ref{rem-interval-support} treats known interval support.',
        r'Throughout this section, the training data, test residuals, and $\theta\ge0$ are fixed. Input and residual cell probabilities give finite primal and dual problems and closed-form bounds. The main results use $\Xi=\mathbb R$; Remark~\ref{rem-interval-support} treats known interval support.', 'section 4 roadmap')
replace('The following proposition expresses the DW ambiguity set through linear constraints on cumulative residual cell probabilities.',
        'The DW band can now be expressed through cell masses.', 'finite-representation lead')
replace(r'Proposition~\ref{prop-finite-rank-constraints} replaces the CDF constraint over all thresholds by $2K$ linear inequalities on residual cell probabilities. The distribution within each cell remains free, and the scalar interval endpoints can be computed by one-dimensional bisection.',
        'Within each cell, the residual distribution remains free. The scalar endpoints can be computed by one-dimensional bisection.', 'finite-representation interpretation')
replace(r'The row equalities in $\mathcal C_\theta$ retain the input cell probabilities, and the cumulative column inequalities impose the DW band. On each product cell, the failure indicator satisfies',
        'To bound the failure objective, compare the indicator on each product cell:', 'cell-objective transition')
replace(r'Residual cells with $j\le2i$ always cause failure for inputs in $\mathcal X_i$, and those with $j\ge2i+2$ are always safe. Only the overlapping interval $\Xi_{2i+1}$ has different upper and lower coefficients. Figure~\ref{fig-joint-partition} illustrates the resulting joint cell structure and the classification of product cells for $K=3$. Thus the cell matrix records the rank constraints exactly, while the failure objective requires the constructions below.',
        r'For inputs in $\mathcal X_i$, the failure status can vary only within $\Xi_{2i+1}$. The other cells are uniformly failing or safe, as illustrated in Figure~\ref{fig-joint-partition} for $K=3$.', 'cell-objective interpretation')
replace(r'The following lemma reduces the Lagrangian duals to $2K$ nonnegative rank multipliers and establishes weak duality.',
        'Lagrangian duality provides finite-dimensional certificates for these bounds.', 'weak-duality lead')
replace(r'Lemma~\ref{lem-weak-duality} gives certificates for the primal extrema through optimization over $2K$ nonnegative rank multipliers. Its equivalent LP forms \eqref{eq-finite-upper-dual} and \eqref{eq-finite-lower-dual} add $K+1$ free variables $z_i$ and $(K+1)(2K+1)$ pairwise inequalities. Each feasible dual choice supplies a bound in the corresponding direction through \eqref{eq-weak-duality}.',
        r'The reduced duals use $2K$ nonnegative multipliers. Their LP forms \eqref{eq-finite-upper-dual} and \eqref{eq-finite-lower-dual} introduce $K+1$ free variables $z_i$ and $(K+1)(2K+1)$ pairwise inequalities.', 'weak-duality interpretation')
replace('The following theorem shows that these dual bounds are exact by constructing feasible joint laws that attain the finite primal objectives.',
        'It remains to realize the cellwise objectives by feasible joint laws.', 'strong-duality lead')
replace(r'Theorem~\ref{thm-finite-dual-reformulations} replaces the search over joint distributions by exact allocations of joint cell probability. The conditional residual assignments retain the full input law, and the equalities also hold with residual atoms, zero-probability input cells, and $\theta=0$.',
        r'The reconstruction retains the full input law and allows residual atoms, zero-probability input cells, and $\theta=0$.', 'strong-duality interpretation')
replace('The following corollary uses the ordering of the cells to evaluate both extrema explicitly and identify optimal certificates with at most one nonzero rank multiplier.',
        'The ordered cells allow the extrema to be evaluated explicitly.', 'closed-form lead')
replace(r'In Corollary~\ref{thm-closed-form-bounds}, the upper bound combines residual mass below an observed value with the probability that the surrogate threshold reaches it. The lower bound measures the overlap required by every admissible coupling.',
        'The upper bound combines the residual mass allowed below a rank with the probability that the input threshold reaches it. The lower bound measures unavoidable overlap.', 'closed-form interpretation')
replace('The following remark incorporates known interval support through additional constraints at its endpoints.',
        'Verified support gives information beyond the empirical residuals.', 'support lead')
replace(r'Remark~\ref{rem-interval-support} separates inputs that fail for every admissible residual, $\hat g(\bm X)\le-b$, from inputs that are always safe, $\hat g(\bm X)>-a$. In particular, $\mathbb P\left\{\hat g(\bm X)\le-a\right\}=0$ rules out failure.',
        r'Inputs with $\hat g(\bm X)\le-b$ must fail; those with $\hat g(\bm X)>-a$ are always safe. Thus $\mathbb P\left\{\hat g(\bm X)\le-a\right\}=0$ rules out failure.', 'support interpretation')

backup = root / 'backups' / ('concise_result_transitions_20261126_' + datetime.now().strftime('%H%M%S'))
backup.mkdir(parents=True)
for name in ['manuscript.tex', 'manuscript.pdf', 'manuscript.aux', 'reference.bib']:
    if (root / name).exists():
        shutil.copy2(root / name, backup / name)
updated = original[:body_start] + body + original[body_end:]
archive = ''.join('%' + line for line in old_body.splitlines(keepends=True))
updated = updated.rstrip('\n') + '\n\n% BEGIN PRESERVED BODY BEFORE CONCISE RESULT TRANSITIONS (2026-11-26)\n'
updated += archive + '% END PRESERVED BODY BEFORE CONCISE RESULT TRANSITIONS\n'
assert path.read_bytes() == original_bytes
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))

def code(text):
    return '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0]
        for line in text.split(r'\end{document}', 1)[0].splitlines())

def blocks(text, names):
    return [match.group(0) for match in re.finditer(r'\\begin\{(' + names + r')\}.*?\\end\{\1\}', code(text), re.S)]

def displays(text):
    return re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation|align)\*?\}.*?\\end\{(?:equation|align)\*?\}', code(text), re.S)

def citations(text):
    return {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', code(text)) for key in group.split(',')}

def prose_word_count(text):
    text = re.sub(r'\$.*?\$', '', text, flags=re.S)
    text = re.sub(r'\\\w+(?:\{[^}]*\})?', '', text)
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", text))

old_words = sum(prose_word_count(edit['before']) for edit in edits)
new_words = sum(prose_word_count(edit['after']) for edit in edits)
active = code(updated)
labels = re.findall(r'\\label\{([^}]+)\}', active)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', active)
report = {
    'backup': str(backup),
    'edited_passages': len(edits),
    'edited_prose_words_before': old_words,
    'edited_prose_words_after': new_words,
    'edited_prose_reduction_percent': round(100 * (old_words - new_words) / old_words, 1),
    'formal_statements_unchanged': blocks(original, 'definition|proposition|lemma|theorem|corollary|remark') == blocks(updated, 'definition|proposition|lemma|theorem|corollary|remark'),
    'proofs_unchanged': blocks(original, 'proof') == blocks(updated, 'proof'),
    'all_displayed_formulas_unchanged': displays(original) == displays(updated),
    'figures_and_captions_unchanged': blocks(original, 'figure') == blocks(updated, 'figure'),
    'preamble_and_frontmatter_unchanged': updated[:body_start] == original[:body_start],
    'previous_body_commented_exactly': ''.join(line[1:] for line in archive.splitlines(keepends=True)) == old_body,
    'existing_comment_archives_preserved': original[body_end:] in updated,
    'citation_keys_unchanged': citations(original) == citations(updated),
    'bibliography_unchanged': (root / 'reference.bib').read_bytes() == (backup / 'reference.bib').read_bytes(),
    'label_order_unchanged': re.findall(r'\\label\{([^}]+)\}', code(original)) == labels,
    'duplicate_labels': [label for label, count in collections.Counter(labels).items() if count > 1],
    'undefined_references': sorted(set(refs) - set(labels)),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', active),
}
Path('tmp/concise_result_transition_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
Path('tmp/concise_result_transition_edits.json').write_text(json.dumps(edits, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
assert all(report[key] for key in ['formal_statements_unchanged', 'proofs_unchanged', 'all_displayed_formulas_unchanged',
    'figures_and_captions_unchanged', 'preamble_and_frontmatter_unchanged', 'previous_body_commented_exactly',
    'existing_comment_archives_preserved', 'citation_keys_unchanged', 'bibliography_unchanged', 'label_order_unchanged'])
assert new_words < old_words
assert not any(report[key] for key in ['duplicate_labels', 'undefined_references', 'manual_sized_delimiters'])
