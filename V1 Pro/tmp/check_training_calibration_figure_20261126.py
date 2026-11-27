"""Check the sampling schematic insertion against the latest author-edited source."""
from collections import Counter
import json
from pathlib import Path
import re

import pymupdf

p = Path(__file__).resolve().parents[1]
before = (p / 'backups/training_calibration_figure_20261126_150518/manuscript_before_final_single_panel.tex').read_text(encoding='utf-8-sig')
after = (p / 'manuscript.tex').read_text(encoding='utf-8-sig')
build = p / 'tmp/training_calibration_figure_20261126'
log = (build / 'manuscript.log').read_text(encoding='utf-8', errors='replace')
aux = (build / 'manuscript.aux').read_text(encoding='utf-8', errors='replace')

equations = lambda s: re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}', s, re.S)
proofs = lambda s: re.findall(r'\\begin\{proof\}(.*?)\\end\{proof\}', s, re.S)
displays = lambda s: re.findall(r'\\\[(.*?)\\\]', s, re.S)
label_list = re.findall(r'\\label\{([^}]+)\}', after)
label_counts = Counter(label_list)
references = set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', after))
figure_paths = re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', after)
caption = re.search(r'\\caption\{(.*?)\}\s*\\label\{fig-training-calibration-sampling\}', after, re.S).group(1)

checks = {
    'numbered_formulas_unchanged': equations(before) == equations(after),
    'unnumbered_display_math_unchanged': displays(before) == displays(after),
    'all_proofs_unchanged': proofs(before) == proofs(after),
    'sections_3_to_5_unchanged': before.split(r'\section{Ambiguity Set Design}', 1)[1] == after.split(r'\section{Ambiguity Set Design}', 1)[1],
    'training_and_calibration_math_preserved': displays(before) == displays(after),
    'figure_count': len(figure_paths),
    'all_graphics_exist': all((p / path).exists() for path in figure_paths),
    'new_figure_defined_once': label_counts['fig-training-calibration-sampling'] == 1,
    'new_figure_referenced': 'fig-training-calibration-sampling' in references,
    'duplicate_labels': [key for key, count in label_counts.items() if count > 1],
    'undefined_source_references': sorted(references - set(label_list)),
    'undefined_build_references': re.findall(r'(?:Reference|Citation) .*?undefined', log),
    'unresolved_build_warnings': re.findall(r'There were undefined|multiply defined|Rerun to get', log),
    'caption_is_single_panel': '(a)' not in caption and '(b)' not in caption and 'panels' not in caption,
    'caption_explains_independence': r'independent of $\mathcal D^{\mathrm{tr}}$' in caption,
    'caption_explains_fixed_surrogate': r'with $\hat g$ fixed' in caption,
    'caption_identifies_schematic': 'illustrative' in caption,
    'aux_new_figure': re.findall(r'\\newlabel\{fig-training-calibration-sampling\}[^\n]*', aux),
    'existing_overfull_warning': re.findall(r'Overfull \\hbox[^\n]*', log),
}
for key in ['numbered_formulas_unchanged', 'unnumbered_display_math_unchanged', 'all_proofs_unchanged', 'sections_3_to_5_unchanged', 'all_graphics_exist', 'new_figure_defined_once', 'new_figure_referenced', 'caption_is_single_panel', 'caption_explains_independence', 'caption_explains_fixed_surrogate', 'caption_identifies_schematic']:
    assert checks[key], (key, checks[key])
for key in ['duplicate_labels', 'undefined_source_references', 'undefined_build_references', 'unresolved_build_warnings']:
    assert not checks[key], (key, checks[key])
assert checks['figure_count'] == 5
with pymupdf.open(build / 'manuscript.pdf') as doc:
    checks['page_count'] = len(doc)
    checks['new_figure_page'] = [i+1 for i, page in enumerate(doc) if 'Training and independent calibration sampling' in ' '.join(page.get_text().split())]
(build / 'source_checks.json').write_text(json.dumps(checks, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(checks, indent=2, ensure_ascii=False))
