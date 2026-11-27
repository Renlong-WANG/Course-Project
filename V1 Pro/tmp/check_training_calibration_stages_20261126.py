from pathlib import Path
import collections
import json
import re

root = Path.cwd()
backup = Path(json.loads(Path('tmp/training_calibration_stages_edits.json').read_text(encoding='utf-8'))['backup'])
old = (backup / 'manuscript.tex').read_text(encoding='utf-8')
new = Path('manuscript.tex').read_text(encoding='utf-8')
old_active, old_tail = old.split(r'\end{document}', 1)
active, tail = new.split(r'\end{document}', 1)

def code(text):
    return '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0] for line in text.splitlines())

def canonical(text):
    return re.sub(r'\s+', '', text)

def numbered(text):
    result = {}
    for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', text, re.S):
        body = match.group(2)
        for label in re.findall(r'\\label\{([^}]+)\}', body):
            result[label] = canonical(body)
    return result

def displays(text):
    expressions = re.findall(r'(?<!\\)\\\[(.*?)\\\]', text, re.S)
    expressions += [match.group(2) for match in re.finditer(
        r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}(.*?)\\end\{\1\}', text, re.S)]
    return collections.Counter(canonical(expression) for expression in expressions)

def cite_keys(text):
    return {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', text)
            for key in group.split(',')}

old_code, new_code = code(old_active), code(active)
section2 = new_code.split(r'\section{Problem Description}', 1)[1].split(r'\section{Ambiguity Set Design}', 1)[0]
section3 = new_code.split(r'\section{Ambiguity Set Design}', 1)[1].split(r'\section{Tractable Reformulation}', 1)[0]
old_section4 = old_active.split(r'\section{Tractable Reformulation}', 1)[1].split(r'\section{Implementation Procedure}', 1)[0]
new_section4 = active.split(r'\section{Tractable Reformulation}', 1)[1].split(r'\section{Implementation Procedure}', 1)[0]
labels = re.findall(r'\\label\{([^}]+)\}', new_code)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', new_code)
bibkeys = set(re.findall(r'@\w+\{([^,]+),', Path('reference.bib').read_text(encoding='utf-8')))
build = Path('tmp/training_calibration_revision_20261126')
aux = (build / 'manuscript.aux').read_text(encoding='utf-8')
baseline_aux = Path('tmp/sampling_stages_baseline_20261126/manuscript.aux').read_text(encoding='utf-8')
aux_labels = dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}', aux))
old_aux_labels = dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}', baseline_aux))
log = (build / 'manuscript.log').read_text(encoding='utf-8', errors='replace')
baseline_log = Path('tmp/sampling_stages_baseline_20261126/manuscript.log').read_text(encoding='utf-8', errors='replace')
data_definition = r'\mathcal D^{\mathrm{te}}:='
residual_definition = r'\xi_j^{\mathrm{te}}:='
proofs = lambda text: re.findall(r'\\begin\{proof\}.*?\\end\{proof\}', text, re.S)
figures = lambda text: re.findall(r'\\begin\{figure\}.*?\\end\{figure\}', text, re.S)
alg = lambda text: re.findall(r'\\begin\{algorithm\}.*?\\end\{algorithm\}', text, re.S)
old_algorithm = alg(old_active)[0]
new_algorithm = alg(active)[0]
report = {
    'numbered_formula_count': len(numbered(new_code)),
    'all_numbered_formulas_and_labels_unchanged': numbered(new_code) == numbered(old_code),
    'all_equation_numbers_unchanged': all(aux_labels[key] == old_aux_labels[key] for key in numbered(new_code)),
    'all_displayed_math_preserved': displays(new_code) == displays(old_code),
    'all_proofs_unchanged': proofs(active) == proofs(old_active),
    'section4_byte_unchanged': new_section4 == old_section4,
    'figures_and_captions_unchanged': figures(active) == figures(old_active),
    'algorithm_steps_unchanged': re.sub(r'^[ \t]*\\Require[^\n]*', '', old_algorithm, flags=re.M)
        == re.sub(r'^[ \t]*\\Require[^\n]*', '', new_algorithm, flags=re.M),
    'test_dataset_defined_once_in_section2': new_code.count(data_definition) == 1 and data_definition in section2,
    'test_residuals_defined_once_in_section2': new_code.count(residual_definition) == 1 and residual_definition in section2,
    'no_dataset_or_residual_redefinitions_in_section3': data_definition not in section3 and residual_definition not in section3,
    'training_freedom_explicit': 'They need not be independent draws from $\\mathbb P$.' in section2
        and 'active learning, or adaptive sampling' in section2,
    'calibration_iid_target_law_explicit': 'independent and identically distributed according to $\\mathbb P$' in section2,
    'surrogate_frozen_during_calibration': 'remains fixed during calibration and reliability assessment' in section2,
    'coverage_proposition_refers_to_section2': 'Under the training and calibration conditions in Section~\\ref{sec-problem}' in section3,
    'preamble_and_introduction_unchanged': old_active.split(r'\section{Problem Description}', 1)[0]
        == active.split(r'\section{Problem Description}', 1)[0],
    'post_document_content_unchanged': tail == old_tail,
    'bibliography_byte_unchanged': Path('reference.bib').read_bytes() == (backup / 'reference.bib').read_bytes(),
    'citation_keys_unchanged': cite_keys(new_code) == cite_keys(old_code),
    'main_sections_unchanged': re.findall(r'\\section\{([^}]+)\}', new_code)
        == re.findall(r'\\section\{([^}]+)\}', old_code),
    'duplicate_labels': [label for label, count in collections.Counter(labels).items() if count > 1],
    'undefined_references': sorted(set(refs) - set(labels)),
    'undefined_citations': sorted(cite_keys(new_code) - bibkeys),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', new_code),
    'reference_or_citation_warnings': [line for line in log.splitlines() if any(word in line.lower()
       for word in ['undefined', 'multiply defined', 'rerun to get cross-references'])],
    'baseline_overfull_warnings': re.findall(r'Overfull[^\n]+', baseline_log),
    'revision_overfull_warnings': re.findall(r'Overfull[^\n]+', log),
    'training_paragraph_start_line': active[:active.index('Evaluating $g$')].count('\n') + 1,
    'calibration_paragraph_start_line': active[:active.index('Residual calibration uses a separate test dataset')].count('\n') + 1,
    'section3_start_line': active[:active.index(r'\section{Ambiguity Set Design}')].count('\n') + 1,
    'built_pdf_bytes': (build / 'manuscript.pdf').stat().st_size,
}
Path('tmp/training_calibration_stages_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
required = [key for key, value in report.items() if isinstance(value, bool)]
assert all(report[key] for key in required)
assert not any(report[key] for key in ['duplicate_labels', 'undefined_references', 'undefined_citations',
    'manual_sized_delimiters', 'reference_or_citation_warnings'])
assert report['revision_overfull_warnings'] == report['baseline_overfull_warnings']
