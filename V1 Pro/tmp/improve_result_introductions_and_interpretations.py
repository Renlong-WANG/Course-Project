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
before = original[body_start:body_end]
body = before
changes = []

def replace_once(old, new, name):
    global body
    assert body.count(old) == 1, (name, body.count(old))
    body = body.replace(old, new, 1)
    changes.append(name)

def introduce(environment, sentence, name):
    token = '\\begin{' + environment + '}'
    assert body.count(token) == 1, (name, body.count(token))
    replace_once(token, sentence + '\n\n' + token, name)

introduce('definition',
    'The following definition uses the corrected discrepancy to constrain the residual CDF simultaneously over all thresholds.',
    'introduce DW definition')
replace_once(
    r'The threshold $\theta$ controls the corrected likelihood discrepancy. The induced CDF tolerances vary across probability levels and can be asymmetric about the empirical CDF. Statistical calibration assigns a confidence level to this set.',
    r'In Definition~\ref{definition-dw-ambiguity-set}, $\theta$ controls the allowed corrected likelihood discrepancy. The induced CDF tolerances vary across probability levels and can be asymmetric about the empirical CDF. Calibrating $\theta$ assigns a confidence level to this simultaneous band.',
    'interpret DW definition')

replace_once(
    r'\begin{proposition}[Finite-sample threshold calibration]',
    r'The following proposition calibrates $\theta$ using the uniform reference statistic and establishes conditional coverage of the true residual law.'
      + '\n\n' + r'\begin{proposition}[Finite-sample threshold calibration]',
    'introduce calibration proposition')

replace_once(
    r'The residual-law coverage in Proposition~\ref{proposition-01} transfers to the failure probability bounds defined in Section~\ref{sec-problem}.',
    r'The following theorem transfers the residual-law coverage in Proposition~\ref{proposition-01} to the upper and lower failure probability bounds.',
    'introduce failure probability theorem')
replace_once(
    r'The same event gives both inequalities, so $1-\delta$ is the confidence level for the entire interval.',
    r'Theorem~\ref{theorem-01} uses the same residual-coverage event for both endpoints, so $1-\delta$ is the confidence level for the entire interval.',
    'interpret joint interval coverage')

replace_once(
    'The same calibrated set can be reused across response thresholds.',
    'The following corollary extends this common coverage event to all response thresholds using the same calibrated ambiguity set.',
    'introduce simultaneous-threshold corollary')
replace_once(
    r'One calibration therefore covers the entire response-threshold curve, including thresholds selected after observing the test data, without an additional confidence allocation across $c$.',
    r'Corollary~\ref{cor-simultaneous-threshold-bounds} gives the entire response-threshold curve from one residual calibration, including thresholds selected after observing the test data, with a common confidence level across $c$.',
    'interpret simultaneous-threshold corollary')

replace_once(
    r'\begin{proposition}[Finite representation of the DW ambiguity set]',
    'The following proposition expresses the DW ambiguity set through linear constraints on cumulative residual cell probabilities.'
      + '\n\n' + r'\begin{proposition}[Finite representation of the DW ambiguity set]',
    'introduce finite-representation proposition')
replace_once(
    r'Each scalar interval can be computed by one-dimensional bisection. Proposition~\ref{prop-finite-rank-constraints} then restricts only the probabilities of the residual cells; the distribution within each cell remains free.',
    r'Proposition~\ref{prop-finite-rank-constraints} replaces the CDF constraint over all thresholds by $2K$ linear inequalities on residual cell probabilities. The distribution within each cell remains free, and the scalar interval endpoints can be computed by one-dimensional bisection.',
    'interpret finite-representation proposition')
replace_once(
    r'On each product cell, the failure indicator satisfies',
    r'The row equalities in $\mathcal C_\theta$ retain the input cell probabilities, and the cumulative column inequalities impose the DW band. On each product cell, the failure indicator satisfies',
    'interpret cell probability polytope')

introduce('lemma',
    r'The following lemma reduces the Lagrangian duals to $2K$ nonnegative rank multipliers and establishes weak duality.',
    'introduce weak-duality lemma')
replace_once(
    r'The duals in \eqref{eq-upper-measure-dual} and \eqref{eq-lower-measure-dual} involve $2K$ nonnegative rank multipliers. Their equivalent LP forms \eqref{eq-finite-upper-dual} and \eqref{eq-finite-lower-dual} add $K+1$ free variables $z_i$ and $(K+1)(2K+1)$ pairwise inequalities. The envelope identities establish these representations before strong duality is invoked.',
    r'Lemma~\ref{lem-weak-duality} gives certificates for the primal extrema through optimization over $2K$ nonnegative rank multipliers. Its equivalent LP forms \eqref{eq-finite-upper-dual} and \eqref{eq-finite-lower-dual} add $K+1$ free variables $z_i$ and $(K+1)(2K+1)$ pairwise inequalities. Each feasible dual choice supplies a bound in the corresponding direction through \eqref{eq-weak-duality}.',
    'interpret weak-duality lemma')
replace_once(
    r'\begin{theorem}[Exact finite reformulations and strong duality]',
    'The following theorem shows that these dual bounds are exact by constructing feasible joint laws that attain the finite primal objectives.'
      + '\n\n' + r'\begin{theorem}[Exact finite reformulations and strong duality]',
    'introduce strong-duality theorem')
replace_once(
    'The finite formulations are exact, and their ordered failure coefficients give a further simplification. The closed-form bounds below follow from cuts between consecutive cells and admit certificates using at most one rank multiplier.',
    r'Theorem~\ref{thm-finite-dual-reformulations} replaces the search over joint distributions by exact allocations of joint cell probability. The conditional residual assignments retain the full input law, and the equalities also hold with residual atoms, zero-probability input cells, and $\theta=0$.'
      + '\n\n'
      + 'The following corollary uses the ordering of the cells to evaluate both extrema explicitly and identify optimal certificates with at most one nonzero rank multiplier.',
    'interpret strong duality and introduce closed forms')

closed_interpretation = ('The upper bound combines residual mass below an observed value with the probability that the surrogate threshold reaches it. '
                         'The lower bound measures the overlap required by every admissible coupling. ')
assert body.count(closed_interpretation) == 1
body = body.replace(closed_interpretation, '', 1)
curve_transition = r'For the response-threshold curves in Corollary~\ref{cor-simultaneous-threshold-bounds}, apply the same construction to $g-c$ and $\hat g-c$.'
replace_once(curve_transition,
    r'In Corollary~\ref{thm-closed-form-bounds}, the upper bound combines residual mass below an observed value with the probability that the surrogate threshold reaches it. The lower bound measures the overlap required by every admissible coupling.'
      + '\n\n' + curve_transition,
    'place closed-form interpretation immediately after proof')

introduce('remark',
    'The following remark incorporates known interval support through additional constraints at its endpoints.',
    'introduce interval-support remark')
support_interpretation = r'Remark~\ref{rem-interval-support} separates inputs that fail for every admissible residual, $\hat g(\bm X)\le-b$, from inputs that are always safe, $\hat g(\bm X)>-a$. In particular, $\mathbb P\left\{\hat g(\bm X)\le-a\right\}=0$ rules out failure.'
replace_once(
    '\\end{remark}\n\nAfter zero failures',
    '\\end{remark}\n\n' + support_interpretation + '\n\nAfter zero failures',
    'interpret interval-support remark')
replace_once(
    r' Verified support can exclude otherwise unobserved failures: in Remark~\ref{rem-interval-support}, $\mathbb P\left\{\hat g(\bm X)\le-a\right\}=0$ rules out failure.',
    '',
    'remove relocated support interpretation')

backup = root / 'backups' / ('result_exposition_style_20261125_' + datetime.now().strftime('%H%M%S'))
backup.mkdir(parents=True)
for name in ['manuscript.tex', 'manuscript.pdf', 'manuscript.aux', 'reference.bib']:
    if (root / name).exists():
        shutil.copy2(root / name, backup / name)
updated = original[:body_start] + body + original[body_end:]
archive = ''.join('%' + line for line in before.splitlines(keepends=True))
updated = updated.rstrip('\n') + '\n\n% BEGIN PRESERVED BODY BEFORE RESULT-EXPOSITION STYLE REVISION (2026-11-25)\n'
updated += archive + '% END PRESERVED BODY BEFORE RESULT-EXPOSITION STYLE REVISION\n'
assert path.read_bytes() == original_bytes
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))

def active_code(text):
    return '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0]
        for line in text.split(r'\end{document}', 1)[0].splitlines())

def environments(text, names):
    return [match.group(0) for match in re.finditer(r'\\begin\{(' + names + r')\}.*?\\end\{\1\}', active_code(text), re.S)]

def displays(text):
    return re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation|align)\*?\}.*?\\end\{(?:equation|align)\*?\}', active_code(text), re.S)

def citations(text):
    return {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', active_code(text))
        for key in group.split(',')}

code = active_code(updated)
labels = re.findall(r'\\label\{([^}]+)\}', code)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', code)
report = {
    'backup': str(backup),
    'prose_changes': changes,
    'formal_result_count': len(environments(updated, 'definition|proposition|lemma|theorem|corollary|remark')),
    'all_formal_statements_unchanged': environments(original, 'definition|proposition|lemma|theorem|corollary|remark') == environments(updated, 'definition|proposition|lemma|theorem|corollary|remark'),
    'all_proofs_unchanged': environments(original, 'proof') == environments(updated, 'proof'),
    'all_displayed_formulas_unchanged': displays(original) == displays(updated),
    'figures_and_captions_unchanged': environments(original, 'figure') == environments(updated, 'figure'),
    'frontmatter_and_section1_unchanged': updated[:body_start] == original[:body_start],
    'all_existing_comments_preserved': original[body_end:] in updated,
    'previous_body_commented_exactly': ''.join(line[1:] for line in archive.splitlines(keepends=True)) == before,
    'citation_keys_unchanged': citations(original) == citations(updated),
    'bibliography_byte_unchanged': (root / 'reference.bib').read_bytes() == (backup / 'reference.bib').read_bytes(),
    'duplicate_labels': [label for label, count in collections.Counter(labels).items() if count > 1],
    'undefined_references': sorted(set(refs) - set(labels)),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', code),
}
Path('tmp/result_exposition_style_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
assert all(report[key] for key in ['all_formal_statements_unchanged', 'all_proofs_unchanged',
    'all_displayed_formulas_unchanged', 'figures_and_captions_unchanged', 'frontmatter_and_section1_unchanged',
    'all_existing_comments_preserved', 'previous_body_commented_exactly', 'citation_keys_unchanged', 'bibliography_byte_unchanged'])
assert report['formal_result_count'] == 9
assert not any(report[key] for key in ['duplicate_labels', 'undefined_references', 'manual_sized_delimiters'])
