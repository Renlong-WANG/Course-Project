from pathlib import Path
import collections
import json
import re

backup = Path(json.loads(Path('tmp/simultaneous_threshold_curves_edits.json').read_text(encoding='utf-8'))['backup'])
old = (backup / 'manuscript.tex').read_text(encoding='utf-8')
new = Path('manuscript.tex').read_text(encoding='utf-8')
marker = '% BEGIN OPTIONAL APPENDIX: INFORMATION CONTENT AND STATISTICAL LIMITS (COMMENTED OUT)'
old_main, old_tail = old.split(marker, 1)
main, tail = new.split(marker, 1)

def code(text):
    return '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0] for line in text.splitlines())

def equations(text):
    result = {}
    for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', text, re.S):
        body = match.group(2)
        canonical = re.sub(r'\s+', '', re.sub(r'\\label\{[^}]+\}', '', body))
        for key in re.findall(r'\\label\{([^}]+)\}', body):
            result[key] = canonical
    return result

def proofs(text):
    return re.findall(r'\\begin\{proof\}.*?\\end\{proof\}', text, re.S)

def cites(text):
    return {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', text)
            for key in group.split(',')}

old_code, active = code(old_main), code(main)
old_equations, new_equations = equations(old_code), equations(active)
labels = re.findall(r'\\label\{([^}]+)\}', active)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', active)
bibkeys = set(re.findall(r'@\w+\{([^,]+),', Path('reference.bib').read_text(encoding='utf-8')))
aux = Path('manuscript.aux').read_text(encoding='utf-8')
aux_labels = dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}', aux))
log = Path('manuscript.log').read_text(encoding='utf-8', errors='replace')
cor_start = main.index(r'\begin{corollary}[Simultaneous bounds across response thresholds]')
proof_start = main.index(r'\begin{proof}', cor_start)
proof_end = main.index(r'\end{proof}', proof_start) + len(r'\end{proof}')
old_proofs_preserved = proofs(main[:proof_start] + main[proof_end:]) == proofs(old_main)
report = {
    'original_29_numbered_formulas_and_labels_preserved': len(old_equations) == 29 and all(new_equations.get(k) == v for k, v in old_equations.items()),
    'numbered_formula_count': len(new_equations),
    'all_equation_numbers_consecutive': sorted(int(aux_labels[k]) for k in new_equations) == list(range(1, 33)),
    'all_six_original_proofs_unchanged': old_proofs_preserved and len(proofs(old_main)) == 6,
    'one_new_proof_added': len(proofs(main)) == 7,
    'commented_appendix_and_all_archives_byte_unchanged': tail == old_tail,
    'bibliography_byte_unchanged': Path('reference.bib').read_bytes() == (backup / 'reference.bib').read_bytes(),
    'citation_keys_unchanged': cites(active) == cites(old_code),
    'only_four_main_sections': len(re.findall(r'\\section\{', active)) == 4,
    'no_active_appendix_or_section5_reference': not re.search(r'\\appendix\b|sec-information', active),
    'duplicate_labels': [key for key, count in collections.Counter(labels).items() if count > 1],
    'undefined_references': sorted(set(refs) - set(labels)),
    'undefined_citations': sorted(cites(active) - bibkeys),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', active),
    'unexpanded_joint_differential': bool(re.search(r'\\mathrm\s*d\s*\\Pi', active)),
    'obsolete_notation': re.findall(r'\\mathscr|\\kappa|\\ell_|r_k|H_k|T\(\\bm x\)|N\s*:=\s*N\^', active),
    'reference_or_citation_warnings': [line for line in log.splitlines()
       if any(word in line.lower() for word in ['undefined', 'multiply defined', 'rerun to get cross-references'])],
    'overfull_warnings': re.findall(r'Overfull[^\n]+', log),
    'corollary_start_line': main[:cor_start].count('\n') + 1,
    'closed_curve_formulas_start_line': main[:main.index('The same formulas give the response-threshold curves')].count('\n') + 1,
    'new_coverage_equation_number': aux_labels['eq-threshold-curve-coverage'],
    'new_closed_curve_equation_numbers': [aux_labels['eq-threshold-closed-upper'], aux_labels['eq-threshold-closed-lower']],
    'pdf_bytes': Path('manuscript.pdf').stat().st_size,
}
Path('tmp/threshold_curves_source_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
required = [key for key, value in report.items() if isinstance(value, bool) and key != 'unexpanded_joint_differential']
assert all(report[key] for key in required)
assert report['numbered_formula_count'] == 32
assert not any(report[key] for key in ['duplicate_labels', 'undefined_references', 'undefined_citations',
    'manual_sized_delimiters', 'unexpanded_joint_differential', 'obsolete_notation', 'reference_or_citation_warnings'])
