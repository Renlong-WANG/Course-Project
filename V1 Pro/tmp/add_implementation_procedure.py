from datetime import datetime
from pathlib import Path
import collections
import json
import re
import shutil

root = Path.cwd()
path = root / 'manuscript.tex'
original_bytes = path.read_bytes()
original = original_bytes.decode('utf-8').replace('\r\n', '\n')
body_start = original.index(r'\section{Problem Description}')
body_end = original.index('% BEGIN OPTIONAL APPENDIX:', body_start)
old_body = original[body_start:body_end]
body = old_body
edits = []

def replace(old, new, purpose):
    global body
    assert body.count(old) == 1, (purpose, body.count(old))
    body = body.replace(old, new, 1)
    edits.append(dict(purpose=purpose, before=old, after=new))

replace(r'Section~\ref{sec-ambiguity-set} constructs the residual ambiguity set and establishes finite-sample coverage of the failure probability bounds, simultaneously across response thresholds. Section~\ref{sec-reformulation} then derives their Lagrangian duals, proves strong duality through a finite reformulation, and obtains closed-form expressions.',
        r'Section~\ref{sec-ambiguity-set} constructs the residual ambiguity set and establishes finite-sample coverage of the failure probability bounds, simultaneously across response thresholds. Section~\ref{sec-reformulation} then derives their Lagrangian duals, proves strong duality through a finite reformulation, and obtains closed-form expressions. Section~\ref{sec-implementation} integrates these results into an existing surrogate modeling workflow.', 'section 2 roadmap')
replace(r'Proposition~\ref{proposition-01} requires no continuity or moment assumptions on the residual law. For fixed $\phi$ and $\psi$, the reference law depends only on $N^{\mathrm{te}}$, so thresholds can be precomputed. \citet{L.J23} give finite-sample evaluation through uniform order-statistic boundary probabilities. A conservative quantile upper bound preserves \eqref{eq-cdf-coverage}.',
        r'Proposition~\ref{proposition-01} requires no continuity or moment assumptions on the residual law. A conservative upper bound on the reference quantile preserves \eqref{eq-cdf-coverage}; its numerical evaluation is described in Section~\ref{sec-implementation}.', 'section 3 calibration computation')
replace(r'Proposition~\ref{prop-finite-rank-constraints} restricts only the residual cell masses, leaving the distribution within each cell free. The scalar endpoints can be computed by one-dimensional bisection.',
        r'Proposition~\ref{prop-finite-rank-constraints} restricts only the residual cell masses, leaving the distribution within each cell free.', 'section 4 endpoint computation')
replace(r'Lemma~\ref{lem-weak-duality} eliminates the function-valued marginal multiplier, leaving $2K$ nonnegative multipliers. The equivalent LPs \eqref{eq-finite-upper-dual} and \eqref{eq-finite-lower-dual} introduce $K+1$ free variables $z_i$ and $(K+1)(2K+1)$ pairwise inequalities.',
        r'Lemma~\ref{lem-weak-duality} eliminates the function-valued marginal multiplier, leaving $2K$ nonnegative multipliers. Equations~\eqref{eq-finite-upper-dual} and \eqref{eq-finite-lower-dual} give equivalent LP forms.', 'section 4 LP size commentary')
replace(r'For the response-threshold curves in Corollary~\ref{cor-simultaneous-threshold-bounds}, applying the same construction to $g-c$ and $\hat g-c$ leaves the residuals, rank counts, and endpoints $l_k,u_k$ unchanged. Only the input partition depends on $c$. Hence, Corollary~\ref{thm-closed-form-bounds} yields',
        r'For a response threshold $c$, applying the construction to $g-c$ and $\hat g-c$ preserves the residuals and rank bounds. Corollary~\ref{thm-closed-form-bounds} therefore gives', 'section 4 threshold curve transition')

implementation = r'''\section{Implementation Procedure}
\label{sec-implementation}

Sections~\ref{sec-problem}--\ref{sec-reformulation} provide the joint model, residual calibration, and closed-form bounds. These results fit into an existing surrogate modeling workflow in three stages. Stage~I is conventional model fitting and selection; Stages~II and III add residual uncertainty calibration and reliability assessment. The workflow's existing independent test data supply the labeled residual sample.

The following algorithm summarizes the three stages for $\Xi=\mathbb R$.

\begin{algorithm}[!htbp]
  \caption{Residual calibration and reliability assessment within a surrogate workflow}
  \label{alg-implementation}
  \small
  \begin{algorithmic}[1]
    \Require Training data $\mathcal D^{\mathrm{tr}}$ for $g$; an existing independent test set $\mathcal D^{\mathrm{te}}$ of fixed size $N^{\mathrm{te}}$; input law $\mathbb P$; confidence parameter $\delta\in(0,1)$; requested response thresholds $c$.
    \Ensure Intervals $\left[\underline p_{\hat f}(c),\overline p_{\hat f}(c)\right]$ at the requested thresholds.
    \Statex \textbf{Stage I. Conventional surrogate modeling}
    \State Fit and select $\hat g$ using only $\mathcal D^{\mathrm{tr}}$, then keep it fixed.
    \Statex \textbf{Stage II. Residual uncertainty calibration}
    \State Obtain $\theta\ge\theta_{N^{\mathrm{te}}}(\delta)$ from the uniform-reference quantile in \eqref{eq-dw-calibrated-threshold}.
    \State Compute $\xi_j^{\mathrm{te}}=g(\bm x_j^{\mathrm{te}})-\hat g(\bm x_j^{\mathrm{te}})$ for $j=1,\ldots,N^{\mathrm{te}}$ using the existing test responses.
    \State Sort the distinct residuals $\xi_{(1)}^{\mathrm{te}}<\cdots<\xi_{(K)}^{\mathrm{te}}$ and compute $c_0,\ldots,c_K$ as in \eqref{eq-dw-counts-and-levels}.
    \State Invert \eqref{eq-dw-rank-acceptance} to obtain $l_k=\alpha_{c_k}(\theta)$ and $u_k=\beta_{c_{k-1}}(\theta)$ for $k=1,\ldots,K$.
    \Statex \textbf{Stage III. Reliability assessment}
    \For{each requested response threshold $c$}
      \State Evaluate the surrogate-response CDF through $\mathbb P\left\{\hat g(\bm X)\le c-\xi_{(k)}^{\mathrm{te}}\right\}$ for $k=1,\ldots,K$.
      \State Compute $\overline p_{\hat f}(c)$ and $\underline p_{\hat f}(c)$ from \eqref{eq-threshold-closed-upper} and \eqref{eq-threshold-closed-lower}.
    \EndFor
  \end{algorithmic}
\end{algorithm}

\emph{Surrogate-model agnostic integration.}
Algorithm~\ref{alg-implementation} uses only surrogate predictions and signed test residuals. Gaussian processes, polynomial chaos expansions, neural networks, and other measurable predictors can therefore use the same calibration and evaluation steps. The fitting method and model architecture remain those of the existing workflow.

\emph{Post-training calibration and data reuse.}
The existing test set can serve both routine prediction assessment and residual calibration, provided it is independent of model fitting and selection. Tuning and early stopping use only $\mathcal D^{\mathrm{tr}}$, including any internal validation splits, and $\hat g$ remains fixed after calibration. When such test data are already available, Stage~II requires no additional evaluations of $g$.

\emph{Calibration numerics.}
For fixed $\phi$ and $\psi$, the reference quantile depends only on $N^{\mathrm{te}}$ and $\delta$ and can be tabulated offline. \citet[Supplement, Section~S.7]{L.J23} compute finite-sample critical values through uniform order-statistic boundary probabilities. For a chosen $\theta$, the scalar endpoints follow by bisection using Proposition~\ref{prop-finite-rank-constraints}; only the observed count levels are needed. Round $\theta$ upward and the acceptance intervals outward to preserve conservatism. If simulation estimates the reference quantile, include its estimation error in the confidence budget.

\emph{Optimization-free evaluation.}
Stage~III uses the scalar rank bounds and surrogate event probabilities directly. It requires no explicit joint partition, cell-mass polytope, or primal or dual LP. The finite reformulations and strong duality establish the sharpness of the closed-form values used by the algorithm. Sorting costs $O\left(N^{\mathrm{te}}\log N^{\mathrm{te}}\right)$; once the event probabilities are available, the two scans cost $O(K)$ per response threshold. Known interval support is incorporated through the endpoint candidates in Remark~\ref{rem-interval-support}.

\emph{Reusable calibration and probability evaluation.}
For fixed $g$, $\hat g$, and $\mathbb P$, Stage~II is reused across the entire response-threshold curve. With exact input event probabilities, Corollary~\ref{cor-simultaneous-threshold-bounds} gives confidence at least $1-\delta$ simultaneously for all $c$, including thresholds selected after calibration. These probabilities can be obtained analytically or estimated by auxiliary simulation evaluating only $\hat g$. For simulation, allocate the total error probability between residual calibration and a simultaneous CDF confidence band based on inputs drawn independently of the test data. Substitute the band's upper probabilities into \eqref{eq-threshold-closed-upper} and its lower probabilities into \eqref{eq-threshold-closed-lower}. Coverage of the entire curve requires the auxiliary band to hold at every real threshold.
'''

replace(r'\section{Implementation Procedure}', implementation, 'section 5 implementation')
backup = root / 'backups' / ('implementation_procedure_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True)
for name in ['manuscript.tex', 'manuscript.pdf', 'manuscript.aux', 'reference.bib']:
    if (root / name).exists():
        shutil.copy2(root / name, backup / name)
updated = original[:body_start] + body + original[body_end:]
assert updated.count(r'\usepackage{needspace}') == 1
updated = updated.replace(r'\usepackage{needspace}', r'\usepackage{needspace}' + '\n' + r'\usepackage{algorithm}' + '\n' + r'\usepackage{algpseudocode}', 1)
archive = ''.join('%' + line for line in old_body.splitlines(keepends=True))
updated = updated.rstrip('\n') + '\n\n% BEGIN PRESERVED BODY BEFORE IMPLEMENTATION PROCEDURE (2026-11-26)\n'
updated += archive + '% END PRESERVED BODY BEFORE IMPLEMENTATION PROCEDURE\n'

def code(text):
    return '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0]
        for line in text.split(r'\end{document}', 1)[0].splitlines())

def blocks(text, names):
    return [m.group(0) for m in re.finditer(r'\\begin\{(' + names + r')\}.*?\\end\{\1\}', code(text), re.S)]

def displays(text):
    return re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation|align)\*?\}.*?\\end\{(?:equation|align)\*?\}', code(text), re.S)

def citations(text):
    return {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', code(text)) for key in group.split(',')}

active = code(updated)
labels = re.findall(r'\\label\{([^}]+)\}', active)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', active)
old_labels = re.findall(r'\\label\{([^}]+)\}', code(original))
report = {
    'backup': str(backup),
    'formal_statements_unchanged': blocks(original, 'definition|proposition|lemma|theorem|corollary|remark') == blocks(updated, 'definition|proposition|lemma|theorem|corollary|remark'),
    'proofs_unchanged': blocks(original, 'proof') == blocks(updated, 'proof'),
    'all_displayed_formulas_unchanged': displays(original) == displays(updated),
    'figures_and_captions_unchanged': blocks(original, 'figure') == blocks(updated, 'figure'),
    'existing_comment_archives_preserved': original[body_end:] in updated,
    'previous_body_commented_exactly': ''.join(line[1:] for line in archive.splitlines(keepends=True)) == old_body,
    'citation_keys_unchanged': citations(original) == citations(updated),
    'bibliography_unchanged': (root / 'reference.bib').read_bytes() == (backup / 'reference.bib').read_bytes(),
    'existing_label_order_unchanged': [label for label in labels if label in old_labels] == old_labels,
    'duplicate_labels': [label for label, count in collections.Counter(labels).items() if count > 1],
    'undefined_references': sorted(set(refs) - set(labels)),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', active),
    'implementation_word_count_approx': len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", re.sub(r'\$.*?\$|\\\w+(?:\[[^\]]*\])?(?:\{[^}]*\})?', '', implementation, flags=re.S))),
}
assert all(report[key] for key in ['formal_statements_unchanged', 'proofs_unchanged', 'all_displayed_formulas_unchanged',
    'figures_and_captions_unchanged', 'existing_comment_archives_preserved', 'previous_body_commented_exactly',
    'citation_keys_unchanged', 'bibliography_unchanged', 'existing_label_order_unchanged'])
assert not any(report[key] for key in ['duplicate_labels', 'undefined_references', 'manual_sized_delimiters'])
assert path.read_bytes() == original_bytes
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))
Path('tmp/implementation_procedure_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
Path('tmp/implementation_procedure_edits.json').write_text(json.dumps(edits, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
