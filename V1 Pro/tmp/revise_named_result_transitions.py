from pathlib import Path
from datetime import datetime
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
    edits.append(dict(purpose=purpose, before=old, after=new))

replace('We use this discrepancy to define the residual ambiguity set.',
        'The following definition constrains the residual law through the corrected CDF discrepancy.', 'definition introduction')
replace(r'We choose $\theta$ from a quantile of this statistic.',
        r'The following proposition calibrates $\theta$ to obtain finite-sample coverage of the residual law.', 'calibration introduction')
replace(r'The guarantee allows atoms and infinite moments. For fixed $\phi$ and $\psi$, the reference law depends only on $N^{\mathrm{te}}$, so thresholds can be precomputed.',
        r'Proposition~\ref{proposition-01} requires no continuity or moment assumptions on the residual law. For fixed $\phi$ and $\psi$, the reference law depends only on $N^{\mathrm{te}}$, so thresholds can be precomputed.', 'calibration interpretation')
replace('Residual-law coverage also controls the failure probability interval.',
        'The following theorem transfers this coverage guarantee to the failure probability interval.', 'failure bounds introduction')
replace(r'For fixed test data, $0\le\theta_1\le\theta_2$ implies $\mathcal Q^{\mathrm{DW}}(\theta_1)\subseteq\mathcal Q^{\mathrm{DW}}(\theta_2)$. The lower bound is nonincreasing and the upper bound nondecreasing in $\theta$, so higher confidence gives a wider or unchanged interval.',
        r'Theorem~\ref{theorem-01} uses one residual-coverage event for both endpoints, so the confidence level applies to the entire interval. For fixed test data, $0\le\theta_1\le\theta_2$ implies $\mathcal Q^{\mathrm{DW}}(\theta_1)\subseteq\mathcal Q^{\mathrm{DW}}(\theta_2)$. The lower bound is nonincreasing and the upper bound nondecreasing in $\theta$, so higher confidence gives a wider or unchanged interval.', 'failure bounds interpretation')
replace('The same coverage event can be used across response thresholds.',
        'The following corollary extends the guarantee to all response thresholds using the same residual ambiguity set.', 'threshold curves introduction')
replace(r'Thresholds may therefore be selected after observing the test data.',
        r'Corollary~\ref{cor-simultaneous-threshold-bounds} permits response thresholds to be selected after observing the test data.', 'threshold curves interpretation')
replace('The DW band can now be expressed through cell masses.',
        'The following proposition expresses the DW ambiguity set through linear constraints on cumulative residual cell probabilities.', 'finite representation introduction')
replace('Within each cell, the residual distribution remains free. The scalar endpoints can be computed by one-dimensional bisection.',
        r'Proposition~\ref{prop-finite-rank-constraints} restricts only the residual cell masses, leaving the distribution within each cell free. The scalar endpoints can be computed by one-dimensional bisection.', 'finite representation interpretation')
replace('Lagrangian duality provides finite-dimensional certificates for these bounds.',
        'The following lemma gives finite-dimensional Lagrangian duals and establishes weak duality.', 'weak duality introduction')
replace(r'The reduced duals use $2K$ nonnegative multipliers. Their LP forms \eqref{eq-finite-upper-dual} and \eqref{eq-finite-lower-dual} introduce $K+1$ free variables $z_i$ and $(K+1)(2K+1)$ pairwise inequalities.',
        r'Lemma~\ref{lem-weak-duality} eliminates the function-valued marginal multiplier, leaving $2K$ nonnegative multipliers. The equivalent LPs \eqref{eq-finite-upper-dual} and \eqref{eq-finite-lower-dual} introduce $K+1$ free variables $z_i$ and $(K+1)(2K+1)$ pairwise inequalities.', 'weak duality interpretation')
replace('It remains to realize the cellwise objectives by feasible joint laws.',
        'The following theorem proves that the finite cell allocations and their duals recover the original failure probability bounds.', 'strong duality introduction')
replace('A finite optimizer specifies the cell masses; the proof supplies their within-cell realization.',
        r'Theorem~\ref{thm-finite-dual-reformulations} reduces the optimization to joint cell masses while retaining the full input law through the within-cell construction.', 'strong duality interpretation')
replace('The ordered cells allow the extrema to be evaluated explicitly.',
        'The following corollary evaluates both bounds in closed form and identifies optimal dual certificates.', 'closed form introduction')
replace('The upper bound combines an allowed residual tail mass with the probability that the input threshold reaches the corresponding observed residual. The lower bound measures unavoidable overlap.',
        r'Corollary~\ref{thm-closed-form-bounds} shows that each residual level gives an upper bound combining allowed tail mass and the probability that the input threshold reaches that level. The lower bound measures unavoidable overlap.', 'closed form interpretation')
replace('Verified support gives information beyond the empirical residuals.',
        'The following remark incorporates known residual support into the bounds.', 'support introduction')
replace(r'Inputs with $\hat g(\bm X)\le-b$ must fail; those with $\hat g(\bm X)>-a$ are always safe. Thus $\mathbb P\left\{\hat g(\bm X)\le-a\right\}=0$ rules out failure.',
        r'Remark~\ref{rem-interval-support} identifies inputs that must fail, $\hat g(\bm X)\le-b$, and those that are always safe, $\hat g(\bm X)>-a$. Thus $\mathbb P\left\{\hat g(\bm X)\le-a\right\}=0$ rules out failure.', 'support interpretation')

backup = root / 'backups' / ('named_result_transitions_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True)
for name in ['manuscript.tex', 'manuscript.pdf', 'manuscript.aux', 'reference.bib']:
    if (root / name).exists():
        shutil.copy2(root / name, backup / name)

updated = original[:body_start] + body + original[body_end:]
archive = ''.join('%' + line for line in old_body.splitlines(keepends=True))
updated = updated.rstrip('\n') + '\n\n% BEGIN PRESERVED BODY BEFORE NAMED RESULT TRANSITIONS (2026-11-26)\n'
updated += archive + '% END PRESERVED BODY BEFORE NAMED RESULT TRANSITIONS\n'

def code(text):
    return '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0]
        for line in text.split(r'\end{document}', 1)[0].splitlines())

def blocks(text, names):
    return [match.group(0) for match in re.finditer(r'\\begin\{(' + names + r')\}.*?\\end\{\1\}', code(text), re.S)]

def displays(text):
    return re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation|align)\*?\}.*?\\end\{(?:equation|align)\*?\}', code(text), re.S)

def citations(text):
    return {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', code(text)) for key in group.split(',')}

active = code(updated)
labels = re.findall(r'\\label\{([^}]+)\}', active)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', active)
result_introductions = []
for match in re.finditer(r'\\begin\{(definition|proposition|lemma|theorem|corollary|remark)\}', active):
    lead = active[:match.start()].strip().split('\n')[-1]
    assert lead.startswith('The following ' + match.group(1) + ' '), (match.group(1), lead)
    result_introductions.append(lead)

report = {
    'backup': str(backup),
    'edited_passages': len(edits),
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
    'result_introductions': result_introductions,
}
assert all(report[key] for key in ['formal_statements_unchanged', 'proofs_unchanged', 'all_displayed_formulas_unchanged',
    'figures_and_captions_unchanged', 'preamble_and_frontmatter_unchanged', 'previous_body_commented_exactly',
    'existing_comment_archives_preserved', 'citation_keys_unchanged', 'bibliography_unchanged', 'label_order_unchanged'])
assert not any(report[key] for key in ['duplicate_labels', 'undefined_references', 'manual_sized_delimiters'])
assert path.read_bytes() == original_bytes
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))
Path('tmp/named_result_transition_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
Path('tmp/named_result_transition_edits.json').write_text(json.dumps(edits, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
