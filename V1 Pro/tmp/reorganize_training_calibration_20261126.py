from datetime import datetime
from pathlib import Path
import json
import shutil

root = Path.cwd()
path = root / 'manuscript.tex'
original_bytes = path.read_bytes()
original = original_bytes.decode('utf-8').replace('\r\n', '\n')
active, archives = original.split(r'\end{document}', 1)
backup = root / 'backups' / ('training_calibration_stages_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir()
for name in ['manuscript.tex', 'manuscript.pdf', 'reference.bib']:
    shutil.copy2(root / name, backup / name)

# Keep the established mathematical definitions verbatim while relocating them.
test_start = active.index('We construct the empirical CDF from a test dataset')
test_display_start = active.index('\\[\n', test_start)
test_display_end = active.index('\\]\n', test_display_start) + len('\\]\n')
test_display = active[test_display_start:test_display_end]
residual_start = active.index('Define the signed test residuals', test_start)
residual_display_start = active.index('\\[\n', residual_start)
residual_display_end = active.index('\\]\n', residual_display_start) + len('\\]\n')
residual_display = active[residual_display_start:residual_display_end]

old_training = r'''Evaluating $g$ can require an expensive high-fidelity simulation. We use the training dataset
\[
  \mathcal D^{\mathrm{tr}}:=\left\{\left(\bm x_i^{\mathrm{tr}},g(\bm x_i^{\mathrm{tr}})\right)\right\}_{i=1}^{N^{\mathrm{tr}}}
\]
to fit a computationally efficient, measurable surrogate $\hat g:=\hat g_{\mathcal D^{\mathrm{tr}}}$. Model fitting and selection use only the training data and are completed before the test data are used. We condition on $\mathcal D^{\mathrm{tr}}$, treat $\hat g$ as fixed, and suppress this dependence in the notation.'''
new_training = r'''Evaluating $g$ can require an expensive high-fidelity simulation. We use the training dataset
\[
  \mathcal D^{\mathrm{tr}}:=\left\{\left(\bm x_i^{\mathrm{tr}},g(\bm x_i^{\mathrm{tr}})\right)\right\}_{i=1}^{N^{\mathrm{tr}}}
\]
to fit a computationally efficient, measurable surrogate $\hat g:=\hat g_{\mathcal D^{\mathrm{tr}}}$. The training inputs may be selected through experimental design, active learning, or adaptive sampling based on previously acquired responses. They need not be independent draws from $\mathbb P$. Such designs can prioritize coverage of $\mathcal X$ or refinement near an estimated limit-state boundary, including regions with low probability under $\mathbb P$. Fitting and model selection use only $\mathcal D^{\mathrm{tr}}$ and are completed before calibration sampling.

Residual calibration uses a separate test dataset
''' + test_display + r'''We fix $N^{\mathrm{te}}\ge1$ before drawing this sample. The test inputs $\bm x_1^{\mathrm{te}},\ldots,\bm x_{N^{\mathrm{te}}}^{\mathrm{te}}$ are independent and identically distributed according to $\mathbb P$ and are independent of $\mathcal D^{\mathrm{tr}}$. Training selection serves surrogate accuracy, while the test sample provides statistical information under the input probability measure that defines $p_f$. The fitted surrogate remains fixed during calibration and reliability assessment. We condition on $\mathcal D^{\mathrm{tr}}$ throughout the analysis and suppress this dependence in the notation.'''
assert active.count(old_training) == 1
active = active.replace(old_training, new_training, 1)

old_law = r'''For a new input $\bm X\sim\mathbb P$ independent of the training data, let $\mathbb Q^\star$ be the distribution of $\xi^\star:=\xi(\bm X)$. Let $\Xi\subseteq\mathbb R$ be a known Borel set with $\mathbb Q^\star(\Xi)=1$; the default choice is $\Xi=\mathbb R$. For any Borel set $\mathcal S$ in a Euclidean space, write $\mathcal B(\mathcal S)$ for its Borel sigma-algebra. Let $\mathcal M_+(\mathcal S)$ denote the finite nonnegative Borel measures concentrated on $\mathcal S$, and let $\mathcal M_1(\mathcal S)$ denote the probability measures.'''
new_law = r'''For a new input $\bm X\sim\mathbb P$ independent of the training data, let $\mathbb Q^\star$ be the conditional distribution of $\xi^\star:=\xi(\bm X)$ given $\mathcal D^{\mathrm{tr}}$. The signed test residuals are
''' + residual_display + r'''Conditional on $\mathcal D^{\mathrm{tr}}$, these residuals are independent and identically distributed according to $\mathbb Q^\star$.

Let $\Xi\subseteq\mathbb R$ be a known Borel set with $\mathbb Q^\star(\Xi)=1$; the default choice is $\Xi=\mathbb R$. For any Borel set $\mathcal S$ in a Euclidean space, write $\mathcal B(\mathcal S)$ for its Borel sigma-algebra. Let $\mathcal M_+(\mathcal S)$ denote the finite nonnegative Borel measures concentrated on $\mathcal S$, and let $\mathcal M_1(\mathcal S)$ denote the probability measures.'''
assert active.count(old_law) == 1
active = active.replace(old_law, new_law, 1)

# Section 3 now starts statistical construction from the data model in Section 2.
section3 = active.index(r'\section{Ambiguity Set Design}')
start = active.index('We construct the empirical CDF from a test dataset', section3)
end = active.index(r'\begin{equation}', start)
active = active[:start] + r'''Using the independent test residuals defined in Section~\ref{sec-problem}, form the empirical CDF
''' + active[end:]
active = active.replace('Before sampling, we fix the divergence parameter',
                        'Before calibration sampling, we fix the divergence parameter', 1)
old = r'Under the sampling conditions stated above, let $\delta\in(0,1)$ and define'
new = r'Under the training and calibration conditions in Section~\ref{sec-problem}, let $\delta\in(0,1)$ and define'
assert active.count(old) == 1
active = active.replace(old, new, 1)
old = r'''Proposition~\ref{proposition-01} requires no continuity or moment assumptions on the residual law. A conservative upper bound on the reference quantile preserves \eqref{eq-cdf-coverage}; its numerical evaluation is described in Section~\ref{sec-implementation}.'''
new = r'''Because Proposition~\ref{proposition-01} conditions on the completed training data, its coverage guarantee accommodates the fixed and adaptive training designs allowed in Section~\ref{sec-problem}. No continuity or moment assumptions on the residual law are required. A conservative upper bound on the reference quantile preserves \eqref{eq-cdf-coverage}; its numerical evaluation is described in Section~\ref{sec-implementation}.'''
assert active.count(old) == 1
active = active.replace(old, new, 1)

# Make the existing workflow refer to the same calibration requirements.
old = 'Once fitting and model selection are complete, an existing independent test set can be used to calibrate residual uncertainty without additional evaluations of $g$.'
new = r'Once fitting and model selection are complete, an existing test set satisfying the calibration sampling conditions in Section~\ref{sec-problem} can be used to calibrate residual uncertainty without additional evaluations of $g$.'
assert active.count(old) == 1
active = active.replace(old, new, 1)
old = r'''\Require Training data $\mathcal D^{\mathrm{tr}}$ for $g$; an existing independent test set $\mathcal D^{\mathrm{te}}$ with size $N^{\mathrm{te}}$ fixed in advance; input law $\mathbb P$; DW calibration error probability $\delta\in(0,1)$; requested response thresholds $c$.'''
new = r'''\Require Training data $\mathcal D^{\mathrm{tr}}$ for $g$; an existing test set $\mathcal D^{\mathrm{te}}$ drawn independently of training with i.i.d. inputs from $\mathbb P$ and size $N^{\mathrm{te}}$ fixed before calibration sampling; input law $\mathbb P$; DW calibration error probability $\delta\in(0,1)$; requested response thresholds $c$.'''
assert active.count(old) == 1
active = active.replace(old, new, 1)

updated = active + r'\end{document}' + archives
assert path.read_bytes() == original_bytes, 'Source changed during preparation.'
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))
report = {'backup': str(backup), 'training_and_calibration_definitions_moved_to_section_2': True,
          'test_residual_definition_moved_to_section_2': True,
          'calibration_conditions_referenced_by_proposition_and_algorithm': True}
Path('tmp/training_calibration_stages_edits.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
