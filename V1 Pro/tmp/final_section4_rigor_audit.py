from pathlib import Path
import collections
import json
import re

root = Path.cwd()
backup = root / 'backups/section4_rigor_audit_20261124_220428'
old = (backup / 'manuscript.tex').read_text(encoding='utf-8')
new = (root / 'manuscript.tex').read_text(encoding='utf-8')
old_active, old_archives = old.split(r'\end{document}', 1)
active, archives = new.split(r'\end{document}', 1)
section_command = r'\section{Tractable Reformulation}'
code = '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0] for line in active.splitlines())

def numbered(text):
    formulas = {}
    for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', text, re.S):
        body = match.group(2)
        canonical = re.sub(r'\s+', '', re.sub(r'\\label\{[^}]+\}', '', body))
        for label in re.findall(r'\\label\{([^}]+)\}', body):
            formulas[label] = canonical
    return formulas

def cites(text):
    return {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', text)
            for key in group.split(',')}

labels = re.findall(r'\\label\{([^}]+)\}', code)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', code)
bibkeys = set(re.findall(r'@\w+\{([^,]+),', (root / 'reference.bib').read_text(encoding='utf-8')))
aux = (root / 'manuscript.aux').read_text(encoding='utf-8')
aux_labels = dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}', aux))
old_aux = (backup / 'manuscript.aux')
header = '% BEGIN PRESERVED SECTION 4 BEFORE RIGOR AUDIT (2026-11-24)\n'
archived_section = archives.split(header, 1)[1].split('% END PRESERVED SECTION 4 BEFORE RIGOR AUDIT', 1)[0]
restored = ''.join(line[1:] for line in archived_section.splitlines(keepends=True))
old_section = old_active[old_active.index(section_command):old_active.index(r'\bibliographystyle')]
log = (root / 'manuscript.log').read_text(encoding='utf-8', errors='replace')
report = {
    'sections_1_to_3_unchanged': new[:new.index(section_command)] == old[:old.index(section_command)],
    'numbered_equation_count': len(numbered(active)),
    'all_numbered_equations_and_labels_unchanged': numbered(active) == numbered(old_active),
    'equation_numbers_consecutive_1_to_29': sorted(int(aux_labels[key]) for key in numbered(active)) == list(range(1, 30)),
    'prior_comment_archives_preserved': old_archives in archives,
    'preaudit_section_archived_exactly': restored == old_section,
    'pre_refinement_closed_form_proof_archived': '% BEGIN PRESERVED CLOSED-FORM PROOF BEFORE STRUCTURAL REFINEMENT (2026-11-24)' in archives,
    'bibliography_byte_unchanged': (root / 'reference.bib').read_bytes() == (backup / 'reference.bib').read_bytes(),
    'citation_keys_unchanged': cites(active) == cites(old_active),
    'duplicate_labels': [key for key, count in collections.Counter(labels).items() if count > 1],
    'undefined_references': sorted(set(refs) - set(labels)),
    'undefined_citations': sorted(cites(code) - bibkeys),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', code),
    'unexpanded_joint_differential': bool(re.search(r'\\mathrm\s*d\s*\\Pi', code)),
    'subsections_or_appendix': bool(re.search(r'\\(?:subsection|appendix)\b', code)),
    'obsolete_notation': re.findall(r'\\mathscr|\\kappa|\\ell_|r_k|H_k|T\(\\bm x\)|N\s*:=\s*N\^', code),
    'build_reference_or_citation_warnings': [line for line in log.splitlines()
        if any(word in line.lower() for word in ['undefined', 'multiply defined', 'rerun to get cross-references'])],
    'overfull_warnings': re.findall(r'Overfull[^\n]+', log),
    'pdf_bytes': (root / 'manuscript.pdf').stat().st_size,
    'section4_start_line': new[:new.index(section_command)].count('\n') + 1,
    'closed_form_proof_start_line': new[:new.index(r'\begin{proof}', new.index(r'\begin{corollary}[Closed-form'))].count('\n') + 1,
}
(root / 'tmp/section4_rigor_final_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2, ensure_ascii=False))
truths = ['sections_1_to_3_unchanged', 'all_numbered_equations_and_labels_unchanged',
          'equation_numbers_consecutive_1_to_29', 'prior_comment_archives_preserved',
          'preaudit_section_archived_exactly', 'pre_refinement_closed_form_proof_archived',
          'bibliography_byte_unchanged', 'citation_keys_unchanged']
assert all(report[key] for key in truths)
assert report['numbered_equation_count'] == 29
empty = ['duplicate_labels', 'undefined_references', 'undefined_citations',
         'manual_sized_delimiters', 'unexpanded_joint_differential',
         'subsections_or_appendix', 'obsolete_notation', 'build_reference_or_citation_warnings']
assert not any(report[key] for key in empty)
