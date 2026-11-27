from pathlib import Path
import collections
import json
import re

report_path = Path('tmp/concise_implementation_checks.json')
report = json.loads(report_path.read_text(encoding='utf-8'))
backup = Path(report['backup'])
original = (backup / 'manuscript.tex').read_text(encoding='utf-8')
current = Path('manuscript.tex').read_text(encoding='utf-8')
start = current.index(r'\section{Implementation Procedure}')
end = current.index('% BEGIN OPTIONAL APPENDIX:', start)
section = current[start:end]

def code(text):
    return '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0] for line in text.split(r'\end{document}', 1)[0].splitlines())

def blocks(text, names):
    return [m.group(0) for m in re.finditer(r'\\begin\{(' + names + r')\}.*?\\end\{\1\}', code(text), re.S)]

def displays(text):
    return re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation|align)\*?\}.*?\\end\{(?:equation|align)\*?\}', code(text), re.S)

active = code(current)
old_active = code(original)
labels = re.findall(r'\\label\{([^}]+)\}', active)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', active)
report['sections_1_to_4_unchanged'] = original[:original.index(r'\section{Implementation Procedure}')] == current[:start]
report['formal_statements_unchanged'] = blocks(original, 'definition|proposition|lemma|theorem|corollary|remark') == blocks(current, 'definition|proposition|lemma|theorem|corollary|remark')
report['proofs_unchanged'] = blocks(original, 'proof') == blocks(current, 'proof')
report['all_displayed_formulas_unchanged'] = displays(original) == displays(current)
report['label_order_unchanged'] = re.findall(r'\\label\{([^}]+)\}', old_active) == labels
report['duplicate_labels'] = [label for label, count in collections.Counter(labels).items() if count > 1]
report['undefined_references'] = sorted(set(refs) - set(labels))
report['manual_sized_delimiters'] = re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', active)
report['implementation_words_after_approx'] = len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", re.sub(r'\$.*?\$|\\\w+(?:\[[^\]]*\])?(?:\{[^}]*\})?', '', section, flags=re.S)))
report['no_run_in_headings'] = r'\emph{' not in section
report['complexity_immediately_after_algorithm'] = section.split(r'\end{algorithm}', 1)[1].lstrip().startswith(r'Algorithm~\ref{alg-implementation}')
report['new_notation_does_not_conflict'] = all(token not in code(current[:start]) for token in [r'\varepsilon', r'N^{\mathrm{aux}}', r'\delta^{\mathrm{aux}}'])
log = Path('manuscript.log').read_text(encoding='utf-8', errors='replace')
report['unresolved_reference_warnings'] = bool(re.search(r'undefined|multiply defined|Label\(s\) may have changed|Rerun to get', log, re.I))
aux = Path('manuscript.aux').read_text(encoding='utf-8')
equations = [(label, int(number)) for label, number in re.findall(r'\\newlabel\{(eq-[^}]+)\}\{\{(\d+)\}', aux)]
report['equation_numbers_unchanged'] = [n for label, n in equations] == list(range(1, 34)) and [label for label, n in equations] == [label for label in re.findall(r'\\label\{([^}]+)\}', old_active) if label.startswith('eq-')]
pages = [p for p in Path('tmp/concise_implementation_layout.txt').read_text(encoding='utf-8').split('\f') if p.strip()]
report['pdf_pages'] = len(pages)
section_page = next(i+1 for i, p in enumerate(pages) if '5. Implementation Procedure' in p)
closing_page = next(i+1 for i, p in enumerate(pages) if 'prescribed overall confidence level' in re.sub(r'\s+', ' ', p))
report['implementation_pages'] = [section_page, closing_page]
report['algorithm_page'] = next(i+1 for i, p in enumerate(pages) if 'Algorithm 1 Residual' in p)
assert all(report[k] for k in ['sections_1_to_4_unchanged', 'formal_statements_unchanged', 'proofs_unchanged', 'all_displayed_formulas_unchanged', 'label_order_unchanged', 'no_run_in_headings', 'complexity_immediately_after_algorithm', 'new_notation_does_not_conflict', 'equation_numbers_unchanged'])
assert not any(report[k] for k in ['duplicate_labels', 'undefined_references', 'manual_sized_delimiters', 'unresolved_reference_warnings'])
assert closing_page - section_page + 1 <= 2
report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
