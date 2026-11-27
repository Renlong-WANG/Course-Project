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
start = original.index(r'\section{Implementation Procedure}')
end = original.index('% BEGIN OPTIONAL APPENDIX:', start)
old_section = original[start:end]
algorithm = re.search(r'\\begin\{algorithm\}.*?\\end\{algorithm\}', old_section, re.S).group(0)
algorithm = algorithm.replace(r'confidence parameter $\delta\in(0,1)$', r'DW calibration error probability $\delta\in(0,1)$')
new_section = r'''\section{Implementation Procedure}
\label{sec-implementation}

The method accepts any measurable surrogate, including Gaussian processes, polynomial chaos expansions, and neural networks. After fitting and model selection are complete, an existing independent test set can calibrate residual uncertainty without further evaluations of $g$. The resulting bounds require no explicit joint partition or LP, and one calibration serves the entire response-threshold curve for fixed $g$, $\hat g$, and $\mathbb P$.

The following algorithm implements Sections~\ref{sec-problem}--\ref{sec-reformulation} for $\Xi=\mathbb R$; Stage~I is already complete when a final surrogate is available.

''' + algorithm + r'''

Algorithm~\ref{alg-implementation} adds $N^{\mathrm{te}}$ surrogate evaluations beyond conventional training. Excluding offline threshold tabulation, residual calibration costs $O\left(N^{\mathrm{te}}\log N^{\mathrm{te}}+K\log(1/\varepsilon)\right)$ scalar operations when bisection uses absolute tolerance $\varepsilon\in(0,1)$. Once the $K$ input event probabilities are available, the two bound scans cost $O(K)$ per response threshold. If an auxiliary sample of size $N^{\mathrm{aux}}$ supplies an empirical CDF, its surrogate responses are evaluated once and sorted in $O\left(N^{\mathrm{aux}}\log N^{\mathrm{aux}}\right)$ time. Subsequent CDF queries and bound scans cost $O\left(K\log\left(1+N^{\mathrm{aux}}\right)\right)$ per threshold, with $O\left(K+N^{\mathrm{aux}}\right)$ storage for the retained rank data and auxiliary responses.

Test data must remain independent of fitting and model selection, and $\hat g$ must remain fixed during and after calibration, as in Section~\ref{sec-problem}. For fixed $\phi$ and $\psi$, reference quantiles can be tabulated by $\left(N^{\mathrm{te}},\delta\right)$ using the finite-sample recursion of \citet[Supplement, Section~S.7]{L.J23}. Conservative numerical evaluation rounds $\theta$ upward, $l_k$ downward, and $u_k$ upward. Verified interval support uses the endpoint adjustments in Remark~\ref{rem-interval-support}.

With exact input probabilities and $\theta\ge\theta_{N^{\mathrm{te}}}(\delta)$, Corollary~\ref{cor-simultaneous-threshold-bounds} gives simultaneous coverage at least $1-\delta$, conditional on $\mathcal D^{\mathrm{tr}}$. Auxiliary simulation should use independent draws from $\mathbb P$, independent of both datasets, and a CDF confidence band valid at every real threshold. Insert its upper probabilities into \eqref{eq-threshold-closed-upper} and its lower probabilities into \eqref{eq-threshold-closed-lower}. A band with conditional error probability at most $\delta^{\mathrm{aux}}$ given both datasets yields coverage at least $1-\delta-\delta^{\mathrm{aux}}$. A simulation-based upper bound on the reference quantile adds its own failure probability to this error budget.

'''

def code(text):
    return '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0] for line in text.split(r'\end{document}', 1)[0].splitlines())

def blocks(text, names):
    return [m.group(0) for m in re.finditer(r'\\begin\{(' + names + r')\}.*?\\end\{\1\}', code(text), re.S)]

def displays(text):
    return re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation|align)\*?\}.*?\\end\{(?:equation|align)\*?\}', code(text), re.S)

def citations(text):
    return {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', code(text)) for key in group.split(',')}

def word_count(text):
    text = re.sub(r'\$.*?\$|\\\w+(?:\[[^\]]*\])?(?:\{[^}]*\})?', '', text, flags=re.S)
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", text))

backup = root / 'backups' / ('concise_implementation_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True)
for name in ['manuscript.tex', 'manuscript.pdf', 'manuscript.aux', 'reference.bib']:
    if (root / name).exists():
        shutil.copy2(root / name, backup / name)
updated = original[:start] + new_section + original[end:]
archive = ''.join('%' + line for line in old_section.splitlines(keepends=True))
updated = updated.rstrip('\n') + '\n\n% BEGIN PRESERVED IMPLEMENTATION BEFORE CONCISE REVISION (2026-11-26)\n'
updated += archive + '% END PRESERVED IMPLEMENTATION BEFORE CONCISE REVISION\n'
active = code(updated)
labels = re.findall(r'\\label\{([^}]+)\}', active)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', active)
old_algorithm = re.search(r'\\begin\{algorithm\}.*?\\end\{algorithm\}', old_section, re.S).group(0)
old_steps = re.findall(r'^\s*\\(?:Statex|State|For|EndFor|Ensure).*$', old_algorithm, re.M)
new_steps = re.findall(r'^\s*\\(?:Statex|State|For|EndFor|Ensure).*$', algorithm, re.M)
report = {
    'backup': str(backup),
    'sections_1_to_4_unchanged': updated[:start] == original[:start],
    'algorithm_steps_unchanged': old_steps == new_steps,
    'algorithm_input_delta_clarified': 'DW calibration error probability' in algorithm,
    'formal_statements_unchanged': blocks(original, 'definition|proposition|lemma|theorem|corollary|remark') == blocks(updated, 'definition|proposition|lemma|theorem|corollary|remark'),
    'proofs_unchanged': blocks(original, 'proof') == blocks(updated, 'proof'),
    'all_displayed_formulas_unchanged': displays(original) == displays(updated),
    'figures_and_captions_unchanged': blocks(original, 'figure') == blocks(updated, 'figure'),
    'existing_comment_archives_preserved': original[end:] in updated,
    'previous_section_commented_exactly': ''.join(line[1:] for line in archive.splitlines(keepends=True)) == old_section,
    'citation_keys_unchanged': citations(original) == citations(updated),
    'bibliography_unchanged': (root / 'reference.bib').read_bytes() == (backup / 'reference.bib').read_bytes(),
    'label_order_unchanged': re.findall(r'\\label\{([^}]+)\}', code(original)) == labels,
    'duplicate_labels': [label for label, count in collections.Counter(labels).items() if count > 1],
    'undefined_references': sorted(set(refs) - set(labels)),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', active),
    'implementation_words_before_approx': word_count(old_section),
    'implementation_words_after_approx': word_count(new_section),
    'no_run_in_headings': r'\emph{' not in new_section,
    'complexity_immediately_after_algorithm': new_section.split(r'\end{algorithm}', 1)[1].lstrip().startswith(r'Algorithm~\ref{alg-implementation}'),
}
assert all(report[key] for key in ['sections_1_to_4_unchanged', 'algorithm_steps_unchanged', 'algorithm_input_delta_clarified',
    'formal_statements_unchanged', 'proofs_unchanged', 'all_displayed_formulas_unchanged', 'figures_and_captions_unchanged',
    'existing_comment_archives_preserved', 'previous_section_commented_exactly', 'citation_keys_unchanged', 'bibliography_unchanged',
    'label_order_unchanged', 'no_run_in_headings', 'complexity_immediately_after_algorithm'])
assert not any(report[key] for key in ['duplicate_labels', 'undefined_references', 'manual_sized_delimiters'])
assert report['implementation_words_after_approx'] < report['implementation_words_before_approx']
assert path.read_bytes() == original_bytes
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))
Path('tmp/concise_implementation_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
