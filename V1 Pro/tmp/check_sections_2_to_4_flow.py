from pathlib import Path
import collections
import json
import re

root = Path.cwd()
backup = Path(json.loads(Path('tmp/sections_2_to_4_flow_edits.json').read_text(encoding='utf-8'))['backup'])
old = (backup / 'manuscript.tex').read_text(encoding='utf-8')
new = Path('manuscript.tex').read_text(encoding='utf-8')
old_active, old_archives = old.split(r'\end{document}', 1)
active, archives = new.split(r'\end{document}', 1)
marker = '% BEGIN OPTIONAL APPENDIX: INFORMATION CONTENT AND STATISTICAL LIMITS (COMMENTED OUT)'
old_main, old_tail = old_active.split(marker, 1)
main, tail = active.split(marker, 1)

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

def proofs(text):
    return re.findall(r'\\begin\{proof\}.*?\\end\{proof\}', text, re.S)

def cites(text):
    return {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', text)
            for key in group.split(',')}

code, old_code = uncommented(active), uncommented(old_active)
labels = re.findall(r'\\label\{([^}]+)\}', code)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', code)
bib = Path('reference.bib').read_text(encoding='utf-8')
bibkeys = re.findall(r'@\w+\{([^,]+),', bib)
aux = Path('manuscript.aux').read_text(encoding='utf-8')
aux_labels = dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}', aux))
log = Path('manuscript.log').read_text(encoding='utf-8', errors='replace')
heading = r'\section{Tractable Reformulation}'
old_section4, new_section4 = old_main.split(heading, 1)[1], main.split(heading, 1)[1]
historical_marker = '% BEGIN PRESERVED SECTIONS 2--4 BEFORE NARRATIVE REVISION (2026-11-24)\n'
saved_main = archives.split(historical_marker, 1)[1].split('% END PRESERVED SECTIONS 2--4 BEFORE NARRATIVE REVISION', 1)[0]
restored_main = ''.join(line[1:] for line in saved_main.splitlines(keepends=True))
report = {
    'original_29_numbered_formulas_and_labels_unchanged': equations(code) == equations(old_code) and len(equations(code)) == 29,
    'original_equation_numbers_unchanged': all(int(aux_labels[key]) == i for i, key in enumerate(equations(code), 1)),
    'section4_all_four_proofs_byte_unchanged': proofs(new_section4) == proofs(old_section4) and len(proofs(new_section4)) == 4,
    'calibration_proof_unchanged': proofs(main)[0] == proofs(old_main)[0],
    'all_six_main_proofs_present': len(proofs(main)) == len(proofs(old_main)) == 6,
    'optional_commented_appendix_and_bibliography_commands_unchanged': tail == old_tail,
    'old_comment_archives_preserved': old_archives in archives,
    'previous_sections_2_to_4_archived_exactly': restored_main == old_main[old_main.index(r'\section{Problem Description}'):],
    'preamble_frontmatter_and_introduction_unchanged': main[:main.index(r'\section{Problem Description}')]
       == old_main[:old_main.index(r'\section{Problem Description}')],
    'bibliography_byte_unchanged': Path('reference.bib').read_bytes() == (backup / 'reference.bib').read_bytes(),
    'citation_keys_preserved': cites(code) == cites(old_code),
    'only_four_main_sections': len(re.findall(r'\\section\{', code)) == 4,
    'appendix_not_compiled': not re.search(r'\\appendix\b', code),
    'no_active_section5_reference': 'sec-information' not in code,
    'duplicate_labels': [key for key, count in collections.Counter(labels).items() if count > 1],
    'undefined_references': sorted(set(refs) - set(labels)),
    'undefined_citations': sorted(cites(code) - set(bibkeys)),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', code),
    'unexpanded_joint_differential': bool(re.search(r'\\mathrm\s*d\s*\\Pi', code)),
    'obsolete_notation': re.findall(r'\\mathscr|\\kappa|\\ell_|r_k|H_k|T\(\\bm x\)|N\s*:=\s*N\^', code),
    'build_reference_or_citation_warnings': [line for line in log.splitlines()
       if any(word in line.lower() for word in ['undefined', 'multiply defined', 'rerun to get cross-references'])],
    'overfull_warnings': re.findall(r'Overfull[^\n]+', log),
    'main_section_start_lines': {title: new[:match.start()].count('\n') + 1
       for match in re.finditer(r'\\section\{([^}]+)\}', main) for title in [match.group(1)]},
    'commented_appendix_start_line': main.count('\n') + 1,
    'pdf_bytes': Path('manuscript.pdf').stat().st_size,
}
Path('tmp/sections_2_to_4_flow_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
required = [key for key, value in report.items() if isinstance(value, bool)
            and key not in ['unexpanded_joint_differential']]
assert all(report[key] for key in required)
assert not any(report[key] for key in ['duplicate_labels', 'undefined_references', 'undefined_citations',
    'manual_sized_delimiters', 'unexpanded_joint_differential', 'obsolete_notation', 'build_reference_or_citation_warnings'])
