from pathlib import Path
import collections
import json
import re

root = Path.cwd()
backup = Path(json.loads(Path('tmp/commented_appendix_backup.json').read_text(encoding='utf-8'))['backup'])
old = (backup / 'manuscript.tex').read_text(encoding='utf-8')
new = Path('manuscript.tex').read_text(encoding='utf-8')
old_active, old_archives = old.split(r'\end{document}', 1)
active, archives = new.split(r'\end{document}', 1)

def uncommented(text):
    return '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0] for line in text.splitlines())

def equations(text):
    result = {}
    for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', text, re.S):
        body = match.group(2)
        canonical = re.sub(r'\s+', '', re.sub(r'\\label\{[^}]+\}', '', body))
        for key in re.findall(r'\\label\{([^}]+)\}', body):
            result[key] = canonical
    return result

old_code, code = uncommented(old_active), uncommented(active)
old_equations, new_equations = equations(old_code), equations(code)
old_main_equations = {key: value for key, value in old_equations.items()
                      if key not in ['eq-target-certification', 'eq-information-limit',
                                     'eq-zero-failure-benchmark', 'eq-paired-evidence-coverage']}
labels = re.findall(r'\\label\{([^}]+)\}', code)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', code)
citations = {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', code)
             for key in group.split(',')}
bibkeys = re.findall(r'@\w+\{([^,]+),', Path('reference.bib').read_text(encoding='utf-8'))
aux = Path('manuscript.aux').read_text(encoding='utf-8')
aux_labels = dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}', aux))
old_section = old_active[old_active.index(r'\section{Information Content'):old_active.index(r'\bibliographystyle')]
header = '% BEGIN OPTIONAL APPENDIX: INFORMATION CONTENT AND STATISTICAL LIMITS (COMMENTED OUT)\n'
block = active.split(header, 1)[1].split('% END OPTIONAL APPENDIX:', 1)[0]
body = block[block.index('%\\appendix\n'):]
restored = ''.join(line[1:] for line in body.splitlines(keepends=True))
assert restored.startswith('\\appendix\n')
log = Path('manuscript.log').read_text(encoding='utf-8', errors='replace')
report = {
    'active_sections': re.findall(r'\\section\{([^}]+)\}', code),
    'only_four_main_sections': len(re.findall(r'\\section\{', code)) == 4,
    'original_29_equations_and_labels_unchanged': new_equations == old_main_equations and len(new_equations) == 29,
    'original_equation_numbers_unchanged': all(int(aux_labels[key]) == i for i, key in enumerate(new_equations, 1)),
    'complete_former_section5_preserved_in_commented_appendix': restored[len('\\appendix\n'):] == old_section,
    'appendix_not_compiled': not re.search(r'\\appendix\b', code),
    'prior_archives_unchanged': archives == old_archives,
    'bibliography_byte_unchanged': Path('reference.bib').read_bytes() == (backup / 'reference.bib').read_bytes(),
    'core_section4_proofs_unchanged': all(a.group(0) == b.group(0) for a, b in zip(
        re.finditer(r'\\begin\{proof\}.*?\\end\{proof\}', old_code.split(r'\section{Tractable Reformulation}', 1)[1].split(r'\section{Information Content', 1)[0], re.S),
        re.finditer(r'\\begin\{proof\}.*?\\end\{proof\}', code.split(r'\section{Tractable Reformulation}', 1)[1], re.S))),
    'duplicate_labels': [key for key, count in collections.Counter(labels).items() if count > 1],
    'undefined_references': sorted(set(refs) - set(labels)),
    'undefined_citations': sorted(citations - set(bibkeys)),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', code),
    'obsolete_section5_references': 'sec-information' in code,
    'reference_or_citation_warnings': [line for line in log.splitlines() if any(word in line.lower()
       for word in ['undefined', 'multiply defined', 'rerun to get cross-references'])],
    'overfull_warnings': re.findall(r'Overfull[^\n]+', log),
    'commented_appendix_start_line': active[:active.index(header)].count('\n') + 1,
    'pdf_bytes': Path('manuscript.pdf').stat().st_size,
}
Path('tmp/commented_appendix_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
assert all(report[key] for key in ['only_four_main_sections', 'original_29_equations_and_labels_unchanged',
    'original_equation_numbers_unchanged', 'complete_former_section5_preserved_in_commented_appendix',
    'appendix_not_compiled', 'prior_archives_unchanged', 'bibliography_byte_unchanged', 'core_section4_proofs_unchanged'])
assert not any(report[key] for key in ['duplicate_labels', 'undefined_references', 'undefined_citations',
    'manual_sized_delimiters', 'obsolete_section5_references', 'reference_or_citation_warnings'])
