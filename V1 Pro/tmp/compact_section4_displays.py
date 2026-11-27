from datetime import datetime
from pathlib import Path
import json
import re
import shutil

root = Path.cwd()
path = root / 'manuscript.tex'
original_bytes = path.read_bytes()
original = original_bytes.decode('utf-8').replace('\r\n', '\n')
start = original.index(r'\section{Tractable Reformulation}')
end = original.index(r'\bibliographystyle', start)
section = original[start:end]
backup = root / 'backups' / ('section4_inline_math_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir()
for name in ['manuscript.tex', 'manuscript.pdf', 'reference.bib']:
    shutil.copy2(root / name, backup / name)

old_input = r'''The input cells and their probabilities are
\[
  \begin{aligned}
    \mathcal X_i&:=\left\{\bm x\in\mathcal X:
      \xi_{(i)}^{\mathrm{te}}\le-\hat g(\bm x)<\xi_{(i+1)}^{\mathrm{te}}\right\},\\
    w_i&:=\mathbb P(\mathcal X_i)
      =H\left(-\xi_{(i)}^{\mathrm{te}}\right)-H\left(-\xi_{(i+1)}^{\mathrm{te}}\right),
      \qquad i=0,\ldots,K.
  \end{aligned}
\]'''
new_input = r'''For $i=0,\ldots,K$, the input cells and their probabilities are
\[
  \mathcal X_i:=\left\{\bm x\in\mathcal X:
    \xi_{(i)}^{\mathrm{te}}\le-\hat g(\bm x)<\xi_{(i+1)}^{\mathrm{te}}\right\},
  \qquad
  w_i:=\mathbb P(\mathcal X_i)
    =H\left(-\xi_{(i)}^{\mathrm{te}}\right)-H\left(-\xi_{(i+1)}^{\mathrm{te}}\right).
\]'''
old_thresholds = r'''\begin{align*}
  \mathbf1_{\{\xi\le -\hat g(\bm x)\}}
  &\le
  \mathbf1_{\{\xi<\xi_{(k)}^{\mathrm{te}}\}}+\mathbf1_{\{\hat g(\bm x)\le-\xi_{(k)}^{\mathrm{te}}\}},\\
  \mathbf1_{\{\xi\le -\hat g(\bm x)\}}
  &\ge
  \mathbf1_{\{\xi\le \xi_{(k)}^{\mathrm{te}}\}}+\mathbf1_{\{\hat g(\bm x)\le-\xi_{(k)}^{\mathrm{te}}\}}-1.
\end{align*}'''
new_thresholds = r'''\[
  \mathbf1_{\{\xi\le\xi_{(k)}^{\mathrm{te}}\}}
    +\mathbf1_{\{\hat g(\bm x)\le-\xi_{(k)}^{\mathrm{te}}\}}-1
  \le\mathbf1_{\{\xi\le-\hat g(\bm x)\}}
  \le\mathbf1_{\{\xi<\xi_{(k)}^{\mathrm{te}}\}}
    +\mathbf1_{\{\hat g(\bm x)\le-\xi_{(k)}^{\mathrm{te}}\}}.
\]'''
old_lagrangian = r'''  \begin{equation*}
    \begin{aligned}
      \mathcal L^+(\Pi,\eta,\bm\lambda,\bm\gamma)
      ={}&\bm\lambda^\top\bm u-\bm\gamma^\top\bm l+\mathbb E_{\mathbb P}\left[\eta(\bm X)\right]\\
      &+\int_{\mathcal X\times\Xi}\left[ \mathbf1_{\{\xi\le-\hat g(\bm x)\}}-\eta(\bm x) -\zeta_{\bm\lambda,\bm\gamma}(\xi) 
      \right]\,\Pi(\mathrm d\bm x,\mathrm d\xi).
    \end{aligned}
  \end{equation*}'''
new_lagrangian = r'''  \begin{equation*}
    \mathcal L^+
    =\bm\lambda^\top\bm u-\bm\gamma^\top\bm l
      +\mathbb E_{\mathbb P}\left[\eta(\bm X)\right]
      +\int_{\mathcal X\times\Xi}\left[
        \mathbf1_{\{\xi\le-\hat g(\bm x)\}}-\eta(\bm x)-\zeta_{\bm\lambda,\bm\gamma}(\xi)
      \right]\,\Pi(\mathrm d\bm x,\mathrm d\xi).
  \end{equation*}'''
old_cells = r'''\begin{equation*}
  \begin{aligned}
    \Xi_{2k}&:=\left\{\xi_{(k)}^{\mathrm{te}}\right\},
      &&k=1,\ldots,K,\\
    \Xi_{2k+1}&:=\left(\xi_{(k)}^{\mathrm{te}},\xi_{(k+1)}^{\mathrm{te}}\right),
      &&k=0,\ldots,K.
  \end{aligned}
\end{equation*}'''
new_cells = r'''\begin{equation*}
  \Xi_{2k}:=\left\{\xi_{(k)}^{\mathrm{te}}\right\}
    \quad\left(k=1,\ldots,K\right),
  \qquad
  \Xi_{2k+1}:=\left(\xi_{(k)}^{\mathrm{te}},\xi_{(k+1)}^{\mathrm{te}}\right)
    \quad\left(k=0,\ldots,K\right).
\end{equation*}'''

changes = [('input_cells_and_weights', old_input, new_input),
           ('threshold_indicator_bounds', old_thresholds, new_thresholds),
           ('collected_lagrangian', old_lagrangian, new_lagrangian),
           ('residual_cell_definitions', old_cells, new_cells)]
for name, old, new in changes:
    assert section.count(old) == 1, (name, section.count(old))
    section = section.replace(old, new, 1)

updated = original[:start] + section + original[end:]
assert path.read_bytes() == original_bytes, 'Source changed during preparation.'
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))

def numbered_formulas(source):
    formulas = {}
    for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', source, re.S):
        body = match.group(2)
        canonical = re.sub(r'\s+', '', re.sub(r'\\label\{[^}]+\}', '', body))
        for label in re.findall(r'\\label\{([^}]+)\}', body):
            formulas[label] = canonical
    return formulas

active = updated.split(r'\end{document}', 1)[0]
old_active = original.split(r'\end{document}', 1)[0]
labels = re.findall(r'\\label\{([^}]+)\}', active)
refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', active)
report = {
    'backup': str(backup),
    'consolidated_displays': [name for name, _, _ in changes],
    'sections_1_to_3_unchanged': updated[:start] == original[:start],
    'bibliography_and_comment_archives_unchanged': updated[updated.index(r'\bibliographystyle'):] == original[end:],
    'all_numbered_formulas_and_labels_unchanged': numbered_formulas(active) == numbered_formulas(old_active),
    'numbered_formulas': len(numbered_formulas(active)),
    'undefined_references': sorted(set(refs) - set(labels)),
}
(root / 'tmp/section4_inline_math_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2, ensure_ascii=True))
assert report['sections_1_to_3_unchanged'] and report['bibliography_and_comment_archives_unchanged']
assert report['all_numbered_formulas_and_labels_unchanged'] and not report['undefined_references']
