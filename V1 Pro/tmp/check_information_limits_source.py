from pathlib import Path
import collections
import json
import re

root = Path.cwd()
backup = Path(json.loads(Path('tmp/information_limits_backup.json').read_text(encoding='utf-8'))['backup'])
old = (backup / 'manuscript.tex').read_text(encoding='utf-8')
new = Path('manuscript.tex').read_text(encoding='utf-8')
active, archives = new.split(r'\end{document}', 1)
old_active, old_archives = old.split(r'\end{document}', 1)
code = '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0] for line in active.splitlines())

def equations(text):
    result = {}
    for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', text, re.S):
        body = match.group(2)
        canonical = re.sub(r'\s+', '', re.sub(r'\\label\{[^}]+\}', '', body))
        for key in re.findall(r'\\label\{([^}]+)\}', body):
            result[key] = canonical
    return result

old_equations, new_equations = equations(old_active), equations(active)
labels = re.findall(r'\\label\{([^}]+)\}', code)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', code)
citation_keys = {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', code)
                 for key in group.split(',')}
bib = Path('reference.bib').read_text(encoding='utf-8')
bibkeys = re.findall(r'@\w+\{([^,]+),', bib)
aux = Path('manuscript.aux').read_text(encoding='utf-8')
aux_labels = dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}', aux))
log = Path('manuscript.log').read_text(encoding='utf-8', errors='replace')
archive = archives.split('% BEGIN PRESERVED ACTIVE MANUSCRIPT BEFORE INFORMATION-LIMIT EXTENSION (2026-11-24)\n', 1)[1]
archive = archive.split('% END PRESERVED ACTIVE MANUSCRIPT BEFORE INFORMATION-LIMIT EXTENSION', 1)[0]
restored = ''.join(line[1:] for line in archive.splitlines(keepends=True))
report = {
    'original_29_numbered_formulas_preserved': all(new_equations.get(k) == v for k, v in old_equations.items()),
    'original_equation_numbers_unchanged': all(int(aux_labels[k]) == i for i, k in enumerate(old_equations, 1)),
    'total_numbered_formulas': len(new_equations),
    'numbered_formulas_consecutive': sorted(int(aux_labels[k]) for k in new_equations) == list(range(1, len(new_equations) + 1)),
    'prior_comment_archives_unchanged': old_archives in archives,
    'previous_active_manuscript_archived_exactly': restored == old_active,
    'ambiguity_set_section_unchanged': old_active.split(r'\section{Ambiguity Set Design}', 1)[1].split(r'\section{Tractable Reformulation}', 1)[0]
       == active.split(r'\section{Ambiguity Set Design}', 1)[1].split(r'\section{Tractable Reformulation}', 1)[0],
    'original_bibliography_entries_preserved': (backup / 'reference.bib').read_text(encoding='utf-8').strip() in bib,
    'duplicate_labels': [key for key, count in collections.Counter(labels).items() if count > 1],
    'duplicate_bibliography_keys': [key for key, count in collections.Counter(bibkeys).items() if count > 1],
    'undefined_references': sorted(set(refs) - set(labels)),
    'undefined_citations': sorted(citation_keys - set(bibkeys)),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', code),
    'unexpanded_joint_differential': bool(re.search(r'\\mathrm\s*d\s*\\Pi', code)),
    'subsections_or_appendix': bool(re.search(r'\\(?:subsection|appendix)\b', code)),
    'reference_or_citation_warnings': [line for line in log.splitlines()
       if any(word in line.lower() for word in ['undefined', 'multiply defined', 'rerun to get cross-references'])],
    'overfull_warnings': re.findall(r'Overfull[^\n]+', log),
    'used_citation_keys': sorted(citation_keys),
    'new_section_start_line': active[:active.index(r'\section{Information Content')].count('\n') + 1,
    'new_theorem_start_line': active[:active.index(r'\begin{theorem}[Information limit')].count('\n') + 1,
    'paired_proposition_start_line': active[:active.index(r'\begin{proposition}[Combining marginal')].count('\n') + 1,
    'pdf_bytes': Path('manuscript.pdf').stat().st_size,
}
Path('tmp/information_limits_source_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
assert all(report[key] for key in ['original_29_numbered_formulas_preserved', 'original_equation_numbers_unchanged',
    'numbered_formulas_consecutive', 'prior_comment_archives_unchanged', 'previous_active_manuscript_archived_exactly',
    'ambiguity_set_section_unchanged', 'original_bibliography_entries_preserved'])
assert report['total_numbered_formulas'] == 33
assert not any(report[key] for key in ['duplicate_labels', 'duplicate_bibliography_keys', 'undefined_references',
    'undefined_citations', 'manual_sized_delimiters', 'unexpanded_joint_differential', 'subsections_or_appendix',
    'reference_or_citation_warnings'])
