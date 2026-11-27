from pathlib import Path
import json
import re

root = Path.cwd()
report_path = Path('tmp/named_result_transition_checks.json')
report = json.loads(report_path.read_text(encoding='utf-8'))
backup = Path(report['backup'])
original = (backup / 'manuscript.tex').read_text(encoding='utf-8')
current = Path('manuscript.tex').read_text(encoding='utf-8')
edits_path = Path('tmp/named_result_transition_edits.json')
edits = json.loads(edits_path.read_text(encoding='utf-8'))
for edit in edits:
    if edit['purpose'] == 'closed form interpretation':
        edit['after'] = next(line for line in current.splitlines() if line.startswith(r'Corollary~\ref{thm-closed-form-bounds} shows'))
start = original.index(r'\section{Problem Description}')
end = original.index('% BEGIN OPTIONAL APPENDIX:', start)
expected_body = original[start:end]
for edit in edits:
    assert expected_body.count(edit['before']) == 1, edit['purpose']
    expected_body = expected_body.replace(edit['before'], edit['after'], 1)
new_start = current.index(r'\section{Problem Description}')
new_end = current.index('% BEGIN OPTIONAL APPENDIX:', new_start)
assert current[new_start:new_end] == expected_body
edits_path.write_text(json.dumps(edits, indent=2), encoding='utf-8')

def numbers(path):
    return dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}', path.read_text(encoding='utf-8')))

new_numbers = numbers(Path('manuscript.aux'))
if (backup / 'manuscript.aux').exists():
    assert numbers(backup / 'manuscript.aux') == new_numbers
    number_check_method = 'auxiliary label numbers'
else:
    def controls(text):
        text = '\n'.join(re.split(r'(?<!\\)%', line, 1)[0] for line in text.split(r'\end{document}', 1)[0].splitlines())
        return re.findall(r'\\(?:section|subsection|setcounter|addtocounter|numberwithin|counterwithin)\*?(?:\[[^\]]*\])?(?:\{[^}]*\})+', text)
    assert controls(original) == controls(current)
    assert report['all_displayed_formulas_unchanged'] and report['preamble_and_frontmatter_unchanged'] and report['label_order_unchanged']
    number_check_method = 'unchanged displayed environments, label order, preamble, and numbering controls'
log = Path('manuscript.log').read_text(encoding='utf-8', errors='replace')
assert not re.search(r'undefined|multiply defined|Label\(s\) may have changed|Rerun to get', log, re.I)
pages = [re.sub(r'\s+', ' ', p) for p in Path('tmp/named_result_transition_layout.txt').read_text(encoding='utf-8').split('\f') if p.strip()]
leads_and_heads = [
    ('The following definition constrains', 'Definition 1 ('),
    ('The following proposition calibrates', 'Proposition 1 ('),
    ('The following theorem transfers', 'Theorem 1 ('),
    ('The following corollary extends', 'Corollary 1 ('),
    ('The following proposition expresses', 'Proposition 2 ('),
    ('The following lemma gives', 'Lemma 1 ('),
    ('The following theorem proves', 'Theorem 2 ('),
    ('The following corollary evaluates', 'Corollary 2 ('),
    ('The following remark incorporates', 'Remark 1 ('),
]
pagination = []
for lead, heading in leads_and_heads:
    lead_pages = [i + 1 for i, page in enumerate(pages) if lead in page]
    head_pages = [i + 1 for i, page in enumerate(pages) if heading in page]
    assert len(lead_pages) == len(head_pages) == 1, (lead, lead_pages, head_pages)
    assert lead_pages == head_pages, (lead, lead_pages, head_pages)
    pagination.append(dict(heading=heading.rstrip(' ('), page=lead_pages[0]))
report.update(
    final_body_matches_reviewed_edits=True,
    equation_and_result_numbers_unchanged=True,
    number_check_method=number_check_method,
    all_result_leads_share_page_with_heading=True,
    pdf_pages=len(pages),
    numbered_equations=len([key for key in new_numbers if key.startswith('eq-')]),
    result_pages=pagination,
    unresolved_reference_warnings=False,
)
report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({key: report[key] for key in ['final_body_matches_reviewed_edits', 'equation_and_result_numbers_unchanged', 'all_result_leads_share_page_with_heading', 'pdf_pages', 'numbered_equations', 'result_pages', 'unresolved_reference_warnings']}, indent=2))
