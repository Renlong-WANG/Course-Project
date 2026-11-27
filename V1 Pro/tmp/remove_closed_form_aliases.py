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
previous_section = original[start:end]
section = previous_section
input_start = section.index('Define the surrogate-response CDF')
input_end = section.index(r'\begin{proposition}', input_start)
input_description = r'''For $i=0,\ldots,K$, the observed residual levels classify inputs by the location of the failure threshold $-\hat g(\bm x)$:
\begin{equation}
  \mathcal X_i:=\left\{\bm x\in\mathcal X:
    \xi_{(i)}^{\mathrm{te}}\le-\hat g(\bm x)<\xi_{(i+1)}^{\mathrm{te}}\right\}.
  \label{eq-input-cells}
\end{equation}
The two partitions satisfy
\[
  \mathcal X=\bigsqcup_{i=0}^{K}\mathcal X_i,
  \qquad
  \Xi=\bigsqcup_{j=1}^{J}\Xi_j.
\]
The input cell probabilities give the surrogate-response threshold probabilities through
\[
  \mathbb P\left\{\hat g(\bm X)\le-\xi_{(k)}^{\mathrm{te}}\right\}
    =\sum_{i=k}^{K}\mathbb P(\mathcal X_i),
  \qquad k=1,\ldots,K.
\]
The half-open convention assigns $-\hat g(\bm x)=\xi_{(k)}^{\mathrm{te}}$ to $\mathcal X_k$. The tail sum therefore includes threshold equalities even when the surrogate response has atoms.

'''
section = section[:input_start] + input_description + section[input_end:]
corollary_start = section.index(r'\begin{corollary}[Closed-form bounds and optimal certificates]')
new_tail = (root / 'tmp/partition_probability_closed_form.tex').read_text(encoding='utf-8').rstrip() + '\n\n\n'
section = section[:corollary_start] + new_tail

backup = root / 'backups' / ('partition_event_probabilities_20261125_' + datetime.now().strftime('%H%M%S'))
backup.mkdir(parents=True)
for name in ['manuscript.tex', 'manuscript.pdf', 'manuscript.aux', 'reference.bib']:
    if (root / name).exists():
        shutil.copy2(root / name, backup / name)
updated = original[:start] + section + original[end:]
archive = ''.join('%' + line for line in previous_section.splitlines(keepends=True))
header = '% BEGIN PRESERVED SECTION 4 BEFORE PARTITION AND EVENT PROBABILITIES (2026-11-25)\n'
updated = updated.rstrip('\n') + '\n\n' + header + archive + '% END PRESERVED SECTION 4 BEFORE PARTITION AND EVENT PROBABILITIES\n'
assert path.read_bytes() == original_bytes
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))

def code(text):
    return '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0]
        for line in text.split(r'\end{document}', 1)[0].splitlines())

def cites(text):
    return {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', code(text))
        for key in group.split(',')}

def numbered(text):
    equations = {}
    for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', code(text), re.S):
        body = match.group(2)
        canonical = re.sub(r'\s+', '', re.sub(r'\\label\{[^}]+\}', '', body))
        for label in re.findall(r'\\label\{([^}]+)\}', body):
            equations[label] = canonical
    return equations

active = code(updated)
labels = re.findall(r'\\label\{([^}]+)\}', active)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', active)
old_equations, new_equations = numbered(original), numbered(updated)
report = {
    'backup': str(backup),
    'sections_1_to_3_unchanged': updated[:start] == original[:start],
    'all_previous_comments_preserved': original[end:] in updated,
    'previous_section_commented_exactly': ''.join(line[1:] for line in archive.splitlines(keepends=True)) == previous_section,
    'numbered_equation_count': len(new_equations),
    'all_previous_equation_labels_retained': set(old_equations) == set(new_equations),
    'equation_labels_with_updated_expressions': [label for label in old_equations if old_equations[label] != new_equations[label]],
    'removed_aliases_remaining': re.findall(r'\bH\b|\b[yY]_[A-Za-z{0-9]|\\bm\s*y\b|\bw_[A-Za-z{0-9]|\\bm\s*w\b', active),
    'duplicate_labels': [label for label, count in collections.Counter(labels).items() if count > 1],
    'undefined_references': sorted(set(refs) - set(labels)),
    'citation_keys_unchanged': cites(original) == cites(updated),
    'bibliography_unchanged': (root / 'reference.bib').read_bytes() == (backup / 'reference.bib').read_bytes(),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', active),
    'subsections_or_active_appendix': bool(re.search(r'\\(?:subsection|appendix)\b', active)),
    'section4_start_line': updated[:start].count('\n') + 1,
}
Path('tmp/partition_event_probability_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
assert all(report[key] for key in ['sections_1_to_3_unchanged', 'all_previous_comments_preserved',
    'previous_section_commented_exactly', 'all_previous_equation_labels_retained', 'citation_keys_unchanged', 'bibliography_unchanged'])
assert set(report['equation_labels_with_updated_expressions']) == {'eq-input-cells', 'eq-dw-closed-upper', 'eq-dw-closed-lower', 'eq-threshold-closed-upper', 'eq-threshold-closed-lower'}
assert not any(report[key] for key in ['removed_aliases_remaining', 'duplicate_labels', 'undefined_references', 'manual_sized_delimiters', 'subsections_or_active_appendix'])
