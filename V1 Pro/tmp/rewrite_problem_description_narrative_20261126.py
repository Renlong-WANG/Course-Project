"""Clarify the sampling-to-ambiguity argument while preserving later derivations."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil

p = Path(__file__).resolve().parents[1]
source = p / 'manuscript.tex'
raw = source.read_bytes()
text = raw.decode('utf-8-sig').replace('\r\n', '\n')
backup = p / 'backups' / ('problem_description_narrative_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True)
for name in ['manuscript.tex', 'manuscript.pdf', 'reference.bib']:
    if (p / name).exists():
        shutil.copy2(p / name, backup / name)

start = text.index(r'\section{Problem Description}')
end = text.index('\nLet $\\Xi', start)
replacement = r'''\section{Problem Description}
\label{sec-problem}

Let $\bm X\sim\mathbb P$ be a random input taking values in $\mathcal X\subseteq\mathbb R^n$, and let $g:\mathcal X\to\mathbb R$ be a measurable limit-state function. The objective of reliability analysis is to evaluate the failure probability
\[
  p_f:=\Pr\{g(\bm X)\le0\}=\int_{\mathcal X}\mathbf 1_{\{g(\bm x)\le0\}}\,\mathbb P(\mathrm d\bm x).
\]

Evaluating $g$ may require computationally expensive high-fidelity simulations. We approximate it by a computationally efficient, measurable surrogate $\hat g:\mathcal X\to\mathbb R$ fitted to the training dataset
\[
  \mathcal D^{\mathrm{tr}}:=\left\{\left(\bm x_i^{\mathrm{tr}},g(\bm x_i^{\mathrm{tr}})\right)\right\}_{i=1}^{N^{\mathrm{tr}}}.
\]
The training inputs may be selected through experimental design, active learning, or adaptive sampling based on previously acquired responses. They need not be drawn from $\mathbb P$ and can target regions that improve surrogate accuracy, including locations near an estimated limit-state boundary. Both fitting and model selection use only $\mathcal D^{\mathrm{tr}}$, yielding the surrogate $\hat g:=\hat g_{\mathcal D^{\mathrm{tr}}}$.

After fitting, we assess surrogate error under the input law $\mathbb P$ using a separate test dataset
\[
  \mathcal D^{\mathrm{te}}:=\left\{\left(\bm x_j^{\mathrm{te}},g(\bm x_j^{\mathrm{te}})\right)\right\}_{j=1}^{N^{\mathrm{te}}}.
\]
The test sample size $N^{\mathrm{te}}\ge1$ is fixed before sampling. The test inputs are independent and identically distributed according to $\mathbb P$ and are independent of $\mathcal D^{\mathrm{tr}}$. The fitted surrogate remains fixed throughout calibration and the subsequent reliability analysis. As illustrated in Figure~\ref{fig-training-calibration-sampling}, training selection targets surrogate accuracy, while independent test sampling supplies the observations used to calibrate residual uncertainty under the input measure defining $p_f$.

\begin{figure}[!t]
  \centering
  \includegraphics[width=0.70\columnwidth]{figures/training_calibration_sampling/fig_training_calibration_sampling.pdf}
  \caption{\textbf{Training and independent calibration sampling.} Blue squares illustrate training inputs selected for space coverage and active refinement near the limit-state boundary. Green circles are iid calibration inputs from $\mathbb P$, independent of $\mathcal D^{\mathrm{tr}}$, with $\hat g$ fixed. Dashed contours show an illustrative input density; shading marks $g(\bm x)\le0$. The geometry and point counts are illustrative.}
  \label{fig-training-calibration-sampling}
\end{figure}

Define the signed residual function
\[
  \xi(\bm x):=g(\bm x)-\hat g(\bm x),\qquad \bm x\in\mathcal X.
\]
For a new input $\bm X\sim\mathbb P$ independent of $\mathcal D^{\mathrm{tr}}$, let $\mathbb Q^\star$ denote the conditional distribution of $\xi^\star:=\xi(\bm X)$ given $\mathcal D^{\mathrm{tr}}$. Throughout the subsequent analysis, we condition on $\mathcal D^{\mathrm{tr}}$ and suppress this dependence in the notation. The test residuals are
\[
  \xi_j^{\mathrm{te}}:=g(\bm x_j^{\mathrm{te}})-\hat g(\bm x_j^{\mathrm{te}}),\qquad j=1,\ldots,N^{\mathrm{te}}.
\]
Conditional on $\mathcal D^{\mathrm{tr}}$, they satisfy
\[
  \xi_1^{\mathrm{te}},\ldots,\xi_{N^{\mathrm{te}}}^{\mathrm{te}}\overset{\mathrm{i.i.d.}}{\sim}\mathbb Q^\star.
\]
A single fitted residual distribution does not express the uncertainty remaining after finitely many test observations. We therefore use these residuals to construct a data-driven ambiguity set of plausible laws, calibrated to contain $\mathbb Q^\star$ with a prescribed confidence level.
'''
text = text[:start] + replacement + text[end:]
old = 'The residual marginal and its dependence on the input jointly determine the failure probability. We represent residual-marginal uncertainty by an ambiguity set $\\mathcal Q$ calibrated to contain $\\mathbb Q^\\star$ with high confidence. For a given $\\mathcal Q$, define the joint ambiguity set'
new = 'The residual marginal and its dependence on the input jointly determine the failure probability. For a residual ambiguity set $\\mathcal Q\\subseteq\\mathcal M_1(\\Xi)$, define the associated joint ambiguity set'
assert text.count(old) == 1
text = text.replace(old, new)
assert text.count(r'\label{sec-problem}') == 1
assert text.count(r'\label{fig-training-calibration-sampling}') == 1
newline = '\r\n' if b'\r\n' in raw else '\n'
source.write_bytes(text.replace('\n', newline).encode('utf-8'))
build = p / 'tmp/problem_description_narrative_20261126'
build.mkdir(parents=True, exist_ok=True)
(build / 'edit_record.json').write_text(json.dumps({'backup': str(backup), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}, indent=2), encoding='utf-8')
print('Updated Section 2; removed the duplicate section heading and restored the sampling schematic.')
print('Backup:', backup.name)
