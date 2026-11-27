from pathlib import Path
import collections
import json
import re

root = Path.cwd()
state = json.loads((root / 'tmp/partition_duality_rewrite_state.json').read_text(encoding='utf-8'))
backup = Path(state['backup'])
old = (backup / 'manuscript.tex').read_text(encoding='utf-8')
new = (root / 'manuscript.tex').read_text(encoding='utf-8')
active, archives = new.split(r'\end{document}', 1)
old_active, old_archives = old.split(r'\end{document}', 1)
code = '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0] for line in active.splitlines())
old_code = '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0] for line in old_active.splitlines())
start = old.index(r'\section{Tractable Reformulation}')
tail = old.index('The same formulas give the response-threshold curves', start)
end = old.index('% BEGIN OPTIONAL APPENDIX:', tail)
header = '% BEGIN PRESERVED SECTION 4 BEFORE PARTITION-BASED DUALITY REWRITE (2026-11-25)\n'
archived = archives.split(header, 1)[1].split('% END PRESERVED SECTION 4 BEFORE PARTITION-BASED DUALITY REWRITE', 1)[0]
restored = ''.join(line[1:] for line in archived.splitlines(keepends=True))
labels = re.findall(r'\\label\{([^}]+)\}', code)
old_labels = re.findall(r'\\label\{([^}]+)\}', old_code)
references = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', code)
def cites(text):
    return {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', text)
            for key in group.split(',')}
bibkeys = set(re.findall(r'@\w+\{([^,]+),', (root / 'reference.bib').read_text(encoding='utf-8')))
aux_labels = dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}', (root / 'manuscript.aux').read_text(encoding='utf-8')))
equation_labels = []
for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', code, re.S):
    equation_labels.extend(re.findall(r'\\label\{([^}]+)\}', match.group(2)))
numbers = sorted(int(aux_labels[label]) for label in equation_labels)
log = (root / 'manuscript.log').read_text(encoding='utf-8', errors='replace')
report = {
    'backup': str(backup),
    'sections_1_to_3_unchanged': new[:start] == old[:start],
    'threshold_curves_discussion_and_existing_comment_archives_unchanged': old[tail:] in new,
    'previous_section_commented_exactly': restored == old[start:end],
    'bibliography_byte_unchanged': (root / 'reference.bib').read_bytes() == (backup / 'reference.bib').read_bytes(),
    'all_previous_labels_retained': set(old_labels).issubset(labels),
    'new_labels': sorted(set(labels) - set(old_labels)),
    'numbered_equations': len(equation_labels),
    'equation_numbers_consecutive': numbers == list(range(1, len(numbers) + 1)),
    'duplicate_labels': [key for key, count in collections.Counter(labels).items() if count > 1],
    'undefined_references': sorted(set(references) - set(labels)),
    'undefined_citations': sorted(cites(code) - bibkeys),
    'citation_keys_preserved': cites(old_code) == cites(code),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', code),
    'old_notation': re.findall(r'\\mathscr|\\kappa|\\ell_|r_k|H_k|T\(\\bm x\)|N\s*:=\s*N\^', code),
    'unexpanded_joint_differential': bool(re.search(r'\\mathrm\s*d\s*\\Pi', code)),
    'subsections_or_active_appendix': bool(re.search(r'\\(?:subsection|appendix)\b', code)),
    'build_reference_warnings': [line for line in log.splitlines()
        if any(fragment in line.lower() for fragment in ['undefined', 'multiply defined', 'rerun to get cross-references'])],
    'overfull_warnings': re.findall(r'Overfull[^\n]+', log),
    'residual_partition_precedes_proposition': active.index(r'\label{eq-residual-cells}') < active.index(r'\begin{proposition}', start),
    'input_partition_precedes_proposition': active.index(r'\label{eq-input-cells}') < active.index(r'\begin{proposition}', start),
    'finite_duals_in_weak_duality_lemma': active.index(r'\begin{lemma}') < active.index(r'\label{eq-finite-upper-dual}') < active.index(r'\end{lemma}'),
    'envelope_identity_in_lemma_proof': active.index(r'\end{lemma}') < active.index(r'\label{eq-dual-envelope-identities}') < active.index(r'\begin{theorem}', start),
    'section4_start_line': new[:start].count('\n') + 1,
    'pdf_bytes': (root / 'manuscript.pdf').stat().st_size,
}
Path('tmp/partition_duality_source_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
truths = ['sections_1_to_3_unchanged', 'threshold_curves_discussion_and_existing_comment_archives_unchanged',
          'previous_section_commented_exactly', 'bibliography_byte_unchanged', 'all_previous_labels_retained',
          'equation_numbers_consecutive', 'citation_keys_preserved', 'residual_partition_precedes_proposition',
          'input_partition_precedes_proposition', 'finite_duals_in_weak_duality_lemma', 'envelope_identity_in_lemma_proof']
assert all(report[key] for key in truths)
empty = ['duplicate_labels', 'undefined_references', 'undefined_citations', 'manual_sized_delimiters',
         'old_notation', 'unexpanded_joint_differential', 'subsections_or_active_appendix', 'build_reference_warnings']
assert not any(report[key] for key in empty)
