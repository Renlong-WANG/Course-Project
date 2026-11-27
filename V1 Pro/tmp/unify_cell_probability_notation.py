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
start = original.index(r'\section{Tractable Reformulation}')
end = original.index('% BEGIN OPTIONAL APPENDIX:', start)
old_section = original[start:end]
section = old_section

# Express both rank events directly through the residual partition.
rank_start = section.index('For any candidate residual law')
rank_end = section.index('Define the surrogate-response CDF', rank_start)
section = section[:rank_start] + r'''For any candidate residual law $\mathbb Q\in\mathcal M_1(\Xi)$, the open rank probability measures mass strictly below an observed residual, while the closed rank probability also includes mass at that value. For $k=1,\ldots,K$, the partition gives
\[
  \mathbb Q\left\{\xi<\xi_{(k)}^{\mathrm{te}}\right\}
    =\sum_{j<2k}\mathbb Q(\Xi_j),
  \qquad
  \mathbb Q\left\{\xi\le\xi_{(k)}^{\mathrm{te}}\right\}
    =\sum_{j\le2k}\mathbb Q(\Xi_j).
\]
The two probabilities differ by the atom mass $\mathbb Q(\Xi_{2k})$.

''' + section[rank_end:]

# Remove the fixed input-cell aliases throughout the active section.
declaration = r'w_i:=\mathbb P(\mathcal X_i)'
assert section.count(declaration) == 1
section = section.replace(declaration, r'\mathbb P(\mathcal X_i)', 1)
old_transport = r'Let $\mathcal T(\bm w,\bm y)$ be the transportation matrices with row sums $\bm w=(w_0,\ldots,w_K)^\top$ and column sums $\bm y$.'
new_transport = r'Let $\mathcal T(\bm y)$ be the set of nonnegative transportation matrices with row sums $\mathbb P(\mathcal X_i)$ and column sums $y_j$.'
assert section.count(old_transport) == 1
section = section.replace(old_transport, new_transport, 1)
section, input_replacements = re.subn(r'\bw_i\b', lambda _: r'\mathbb P(\mathcal X_i)', section)
section = section.replace(r'\mathcal T(\bm w,\bm y)', r'\mathcal T(\bm y)')

# Use measure continuity for the endpoint step, without introducing CDF left limits.
para_start = section.index(r'  For $k=1,\ldots,K-1$, the empirical CDF')
para_end = section.index('\n\n', para_start)
section = section[:para_start] + r'''  For $k=1,\ldots,K-1$, the empirical CDF on $\left[\xi_{(k)}^{\mathrm{te}},\xi_{(k+1)}^{\mathrm{te}}\right)$ equals $c_k/N^{\mathrm{te}}$. Monotonicity makes the lower band constraint on this interval equivalent to $\mathbb Q\left\{\xi\le\xi_{(k)}^{\mathrm{te}}\right\}\ge\alpha_{c_k}(\theta)$. By continuity of probability from below, the upper band constraint is equivalent to $\mathbb Q\left\{\xi<\xi_{(k+1)}^{\mathrm{te}}\right\}\le\beta_{c_k}(\theta)$. The exterior intervals give $\mathbb Q\left\{\xi<\xi_{(1)}^{\mathrm{te}}\right\}\le\beta_0(\theta)$ and $\mathbb Q\left\{\xi\le\xi_{(K)}^{\mathrm{te}}\right\}\ge\alpha_{N^{\mathrm{te}}}(\theta)$; their other band constraints are automatic because $\alpha_0(\theta)=0$ and $\beta_{N^{\mathrm{te}}}(\theta)=1$. The partition identities above then yield \eqref{eq-finite-rank-constraints}.''' + section[para_end:]

backup = root / 'backups' / ('direct_cell_probabilities_20261125_' + datetime.now().strftime('%H%M%S'))
backup.mkdir(parents=True)
for name in ['manuscript.tex', 'manuscript.pdf', 'manuscript.aux']:
    shutil.copy2(root / name, backup / name)
updated = original[:start] + section + original[end:]
archive = ''.join('%' + line for line in old_section.splitlines(keepends=True))
updated = updated.rstrip('\n') + '\n\n% BEGIN PRESERVED SECTION 4 BEFORE DIRECT CELL-PROBABILITY NOTATION (2026-11-25)\n'
updated += archive + '% END PRESERVED SECTION 4 BEFORE DIRECT CELL-PROBABILITY NOTATION\n'
assert path.read_bytes() == original_bytes
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))

def code(text):
    return '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0]
        for line in text.split(r'\end{document}', 1)[0].splitlines())

def equations(text, translate=False):
    result = {}
    for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', code(text), re.S):
        body = match.group(2)
        if translate:
            body = body.replace(declaration, r'\mathbb P(\mathcal X_i)')
            body = re.sub(r'\bw_i\b', lambda _: r'\mathbb P(\mathcal X_i)', body)
        canonical = re.sub(r'\s+', '', re.sub(r'\\label\{[^}]+\}', '', body))
        for label in re.findall(r'\\label\{([^}]+)\}', body):
            result[label] = canonical
    return result

active = code(updated)
labels = re.findall(r'\\label\{([^}]+)\}', active)
refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', active)
report = {
    'backup': str(backup),
    'input_probability_aliases_replaced': input_replacements,
    'numbered_equations_changed_only_by_requested_notation': equations(original, translate=True) == equations(updated),
    'numbered_equation_count': len(equations(updated)),
    'sections_1_to_3_unchanged': updated[:start] == original[:start],
    'all_existing_comment_archives_preserved': original[end:] in updated,
    'previous_section_commented_exactly': ''.join(line[1:] for line in archive.splitlines(keepends=True)) == old_section,
    'remaining_input_probability_aliases': re.findall(r'\bw_[A-Za-z0-9{]|\\bm\s*w\b', active),
    'cdf_left_limit_notation_or_definition': bool(re.search(r'F_\{\\mathbb Q\}\([^)]*-|\\mathrm\{te\}-\\right|CDF left limit|s\\uparrow t', active)),
    'duplicate_labels': [label for label, count in collections.Counter(labels).items() if count > 1],
    'undefined_references': sorted(set(refs) - set(labels)),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', active),
    'section4_start_line': updated[:start].count('\n') + 1,
}
Path('tmp/direct_cell_probability_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
assert all(report[key] for key in ['numbered_equations_changed_only_by_requested_notation',
    'sections_1_to_3_unchanged', 'all_existing_comment_archives_preserved', 'previous_section_commented_exactly'])
assert not any(report[key] for key in ['remaining_input_probability_aliases', 'cdf_left_limit_notation_or_definition',
    'duplicate_labels', 'undefined_references', 'manual_sized_delimiters'])
