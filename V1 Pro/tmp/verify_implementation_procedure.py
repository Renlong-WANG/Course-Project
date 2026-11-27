from pathlib import Path
import collections
import json
import re

report_path = Path('tmp/implementation_procedure_checks.json')
report = json.loads(report_path.read_text(encoding='utf-8'))
backup = Path(report['backup'])
original = (backup / 'manuscript.tex').read_text(encoding='utf-8')
current = Path('manuscript.tex').read_text(encoding='utf-8')

def code(text):
    return '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0] for line in text.split(r'\end{document}', 1)[0].splitlines())

def blocks(text, names):
    return [m.group(0) for m in re.finditer(r'\\begin\{(' + names + r')\}.*?\\end\{\1\}', code(text), re.S)]

def displays(text):
    return re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation|align)\*?\}.*?\\end\{(?:equation|align)\*?\}', code(text), re.S)

active = code(current)
old_active = code(original)
report['formal_statements_unchanged'] = blocks(original, 'definition|proposition|lemma|theorem|corollary|remark') == blocks(current, 'definition|proposition|lemma|theorem|corollary|remark')
report['proofs_unchanged'] = blocks(original, 'proof') == blocks(current, 'proof')
report['all_displayed_formulas_unchanged'] = displays(original) == displays(current)
report['figures_and_captions_unchanged'] = blocks(original, 'figure') == blocks(current, 'figure')
labels = re.findall(r'\\label\{([^}]+)\}', active)
old_labels = re.findall(r'\\label\{([^}]+)\}', old_active)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', active)
report['existing_label_order_unchanged'] = [label for label in labels if label in old_labels] == old_labels
report['duplicate_labels'] = [label for label, count in collections.Counter(labels).items() if count > 1]
report['undefined_references'] = sorted(set(refs) - set(labels))
report['manual_sized_delimiters'] = re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', active)
forbidden = [r'\$H\b', r'\by_j\b', r'\bY_j\b', r'\$N\s*[:=]']
implementation = active.split(r'\section{Implementation Procedure}', 1)[1]
report['new_section_preserves_notation'] = not any(re.search(pattern, implementation) for pattern in forbidden)
report['existing_comment_archives_preserved'] = original[original.index('% BEGIN OPTIONAL APPENDIX:'):] in current
log = Path('manuscript.log').read_text(encoding='utf-8', errors='replace')
report['unresolved_reference_warnings'] = bool(re.search(r'undefined|multiply defined|Label\(s\) may have changed|Rerun to get', log, re.I))
pages = [p for p in Path('tmp/implementation_procedure_layout.txt').read_text(encoding='utf-8').split('\f') if p.strip()]
section_page = next(i+1 for i,p in enumerate(pages) if '5. Implementation Procedure' in p)
algorithm_page = next(i+1 for i,p in enumerate(pages) if 'Algorithm 1 Residual' in p)
closing_page = next(i+1 for i,p in enumerate(pages) if 'Coverage of the entire curve requires' in re.sub(r'\s+', ' ', p))
report['pdf_pages'] = len(pages)
report['implementation_pages'] = [section_page, closing_page]
report['algorithm_page'] = algorithm_page
report['algorithm_precedes_considerations'] = current.index(r'\end{algorithm}') < current.index(r'\emph{Surrogate-model agnostic integration.}') and algorithm_page == section_page
aux = Path('manuscript.aux').read_text(encoding='utf-8')
eq_numbers = [(key, int(number)) for key, number in re.findall(r'\\newlabel\{(eq-[^}]+)\}\{\{(\d+)\}', aux)]
report['numbered_equations'] = len(eq_numbers)
report['equation_numbers_unchanged'] = [number for key, number in eq_numbers] == list(range(1, 34)) and [key for key, number in eq_numbers] == [key for key in old_labels if key.startswith('eq-')]
report['all_stages_present'] = all('Stage ' + stage + '.' in pages[algorithm_page-1] for stage in ['I', 'II', 'III'])
assert all(report[key] for key in ['formal_statements_unchanged', 'proofs_unchanged', 'all_displayed_formulas_unchanged', 'figures_and_captions_unchanged', 'existing_label_order_unchanged', 'existing_comment_archives_preserved', 'new_section_preserves_notation', 'algorithm_precedes_considerations', 'equation_numbers_unchanged', 'all_stages_present'])
assert not any(report[key] for key in ['duplicate_labels', 'undefined_references', 'manual_sized_delimiters', 'unresolved_reference_warnings'])
assert closing_page - section_page + 1 <= 2
report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
