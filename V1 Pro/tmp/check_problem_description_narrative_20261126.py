"""Check the Section 2 narrative revision without altering the mathematical results."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

import pymupdf

p = Path(__file__).resolve().parents[1]
build = p / 'tmp/problem_description_narrative_20261126'
record = json.loads((build / 'edit_record.json').read_text(encoding='utf-8'))
backup = Path(record['backup'])
before = (backup / 'manuscript.tex').read_text(encoding='utf-8-sig')
after = (p / 'manuscript.tex').read_text(encoding='utf-8-sig')
assert hashlib.sha256((p / 'manuscript.tex').read_bytes()).hexdigest() == record['source_sha256'], 'Source changed after build preparation'
log = (build / 'manuscript.log').read_text(encoding='utf-8', errors='replace')
labels = Counter(re.findall(r'\\label\{([^}]+)\}', after))
refs = set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', after))
equations = lambda s: re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}', s, re.S)
proofs = lambda s: re.findall(r'\\begin\{proof\}(.*?)\\end\{proof\}', s, re.S)
checks = {
    'numbered_equations_unchanged': equations(before) == equations(after),
    'proofs_unchanged': proofs(before) == proofs(after),
    'sections_3_to_5_unchanged': before.split(r'\section{Ambiguity Set Design}', 1)[1] == after.split(r'\section{Ambiguity Set Design}', 1)[1],
    'bibliography_unchanged': (backup / 'reference.bib').read_bytes() == (p / 'reference.bib').read_bytes(),
    'section_titles': re.findall(r'\\section\{([^}]+)\}', after),
    'one_problem_description_heading': after.count(r'\section{Problem Description}') == 1,
    'one_problem_description_label': labels['sec-problem'] == 1,
    'one_sampling_figure': labels['fig-training-calibration-sampling'] == 1,
    'sampling_figure_referenced': 'fig-training-calibration-sampling' in refs,
    'figure_assets_exist': all((p / x).exists() for x in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', after)),
    'duplicates': [x for x, n in labels.items() if n > 1],
    'undefined_references': sorted(refs - set(labels)),
    'unresolved_build_warnings': re.findall(r'(?:Reference|Citation) .*?undefined|There were undefined|multiply defined|Rerun to get', log),
    'overfull_warnings': re.findall(r'Overfull \\hbox[^\n]*', log),
    'calibration_iid_statement': r'\overset{\mathrm{i.i.d.}}{\sim}\mathbb Q^\star' in after,
    'no_manually_sized_delimiters_in_new_section': not re.search(r'\\(?:big|Big|bigg|Bigg)[lrm]?', after.split(r'\section{Problem Description}', 1)[1].split(r'\section{Ambiguity Set Design}', 1)[0]),
}
for key in ['numbered_equations_unchanged', 'proofs_unchanged', 'sections_3_to_5_unchanged', 'bibliography_unchanged', 'one_problem_description_heading', 'one_problem_description_label', 'one_sampling_figure', 'sampling_figure_referenced', 'figure_assets_exist', 'calibration_iid_statement', 'no_manually_sized_delimiters_in_new_section']:
    assert checks[key], key
for key in ['duplicates', 'undefined_references', 'unresolved_build_warnings']:
    assert not checks[key], (key, checks[key])
assert len(checks['section_titles']) == 5
with pymupdf.open(build / 'manuscript.pdf') as doc:
    checks['page_count'] = len(doc)
    keys = ['Training and independent calibration sampling', 'KL and DW acceptance regions', 'Simultaneous confidence band', 'Residual and input partitions', 'Joint cell partition']
    checks['figure_locations'] = [{'caption': k, 'page': i+1} for i, pg in enumerate(doc) for k in keys if k in ' '.join(pg.get_text().split())]
    for i in range(3):
        doc[i].get_pixmap(matrix=pymupdf.Matrix(1.8, 1.8), alpha=False).save(build / f'manuscript_page_{i+1:02}.png')
(build / 'checks.json').write_text(json.dumps(checks, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(checks, indent=2, ensure_ascii=False))
