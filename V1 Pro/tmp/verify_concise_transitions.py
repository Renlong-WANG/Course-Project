from pathlib import Path
import json
import re
import collections

root = Path.cwd()
path = root / 'manuscript.tex'
old_report = json.loads(Path('tmp/concise_result_transition_checks.json').read_text(encoding='utf-8'))
backup = Path(old_report['backup'])
original = (backup / 'manuscript.tex').read_text(encoding='utf-8')
updated = path.read_text(encoding='utf-8')
body_start = original.index(r'\section{Problem Description}')
body_end = original.index('% BEGIN OPTIONAL APPENDIX:', body_start)
old_body = original[body_start:body_end]
marker = '% BEGIN PRESERVED BODY BEFORE CONCISE RESULT TRANSITIONS (2026-11-26)\n'
archive = updated.split(marker, 1)[1].split('% END PRESERVED BODY BEFORE CONCISE RESULT TRANSITIONS', 1)[0]
edits = json.loads(Path('tmp/concise_result_transition_edits.json').read_text(encoding='utf-8'))
final_passages = {
    'calibration lead': r'We choose $\theta$ from a quantile of this statistic.',
    'strong-duality interpretation': r'A finite optimizer specifies the cell masses; the proof supplies their within-cell realization.',
    'definition interpretation': r'The induced CDF tolerances vary by probability level and can be asymmetric about the empirical CDF. Calibration links $\theta$ to a confidence level.',
    'threshold-coverage interpretation': r'Thresholds may therefore be selected after observing the test data. Complementing the endpoints gives simultaneous bounds on $\Pr \left\{g(\bm X)>c\right\}$. The functions $g$, $\hat g$, and the law $\mathbb P$ remain fixed; fragility curves conditioned on hazard intensity require coverage for the corresponding conditional residual laws.',
    'closed-form interpretation': r'The upper bound combines an allowed residual tail mass with the probability that the input threshold reaches the corresponding observed residual. The lower bound measures unavoidable overlap.',
}
for edit in edits:
    if edit['purpose'] in final_passages:
        edit['after'] = final_passages[edit['purpose']]
    assert updated[:updated.index(r'\end{document}')].count(edit['after']) == 1, edit['purpose']

verification = Path('tmp/tighten_result_transitions.py').read_text(encoding='utf-8')
exec(verification[verification.index('def code(text):'):])
pages = [re.sub(r'\s+', ' ', page) for page in Path('tmp/concise_result_transition_layout.txt').read_text(encoding='utf-8').split('\f') if page.strip()]
leads_and_heads = [
    ('We use this discrepancy', 'Definition 1 ('),
    ('from a quantile of this statistic.', 'Proposition 1 ('),
    ('Residual-law coverage also controls', 'Theorem 1 ('),
    ('The same coverage event can', 'Corollary 1 ('),
    ('The DW band can now', 'Proposition 2 ('),
    ('Lagrangian duality provides', 'Lemma 1 ('),
    ('It remains to realize', 'Theorem 2 ('),
    ('The ordered cells allow', 'Corollary 2 ('),
    ('Verified support gives', 'Remark 1 ('),
]
pagination = []
for lead, heading in leads_and_heads:
    lead_pages = [i+1 for i, page in enumerate(pages) if lead in page]
    head_pages = [i+1 for i, page in enumerate(pages) if heading in page]
    assert len(lead_pages) == len(head_pages) == 1, (lead, lead_pages, head_pages)
    assert lead_pages == head_pages, (lead, lead_pages, head_pages)
    pagination.append({'heading': heading.rstrip(' ('), 'page': lead_pages[0]})
report['pdf_pages'] = len(pages)
report['all_result_leads_share_page_with_heading'] = True
report['result_pages'] = pagination
report['numbered_equations'] = len(re.findall(r'\\newlabel\{eq-[^}]+\}', Path('manuscript.aux').read_text(encoding='utf-8')))
report['log_has_unresolved_references'] = bool(re.search(r'undefined|multiply defined|Label\(s\) may have changed|Rerun to get', Path('manuscript.log').read_text(encoding='utf-8', errors='replace'), re.I))
assert not report['log_has_unresolved_references']
Path('tmp/concise_result_transition_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'pagination': pagination, 'pdf_pages': len(pages), 'numbered_equations': report['numbered_equations']}))
