from datetime import datetime
from pathlib import Path
import json
import re
import shutil

root = Path.cwd()
path = root / 'manuscript.tex'
original_bytes = path.read_bytes()
original = original_bytes.decode('utf-8').replace('\r\n', '\n')
marker = '% BEGIN OPTIONAL APPENDIX: INFORMATION CONTENT AND STATISTICAL LIMITS (COMMENTED OUT)'
main, protected = original.split(marker, 1)
old_main = main
backup = root / 'backups' / ('sections_2_to_4_flow_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir()
for name in ['manuscript.tex', 'manuscript.pdf', 'reference.bib']:
    shutil.copy2(root / name, backup / name)
changes = []

def paragraph(prefix, replacement):
    global main
    lines = main.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if line.lstrip().startswith(prefix)]
    assert len(matches) == 1, (prefix, len(matches))
    i = matches[0]
    indentation = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
    lines[i] = indentation + replacement.strip() + '\n' if replacement else ''
    main = ''.join(lines)
    changes.append(prefix)

# Section 2 defines the information model and the two optimization objectives.
paragraph(r'For fixed $g$, this functional is linear in', '')
paragraph(r'The failure probability depends on the residual law', r'''The residual marginal and its dependence on the input jointly determine the failure probability. We represent residual-marginal uncertainty by an ambiguity set $\mathcal Q$ calibrated to contain $\mathbb Q^\star$ with high confidence. For a given $\mathcal Q$, define the joint ambiguity set''')
paragraph(r'The joint ambiguity set allows all dependence structures', r'''The true residual is determined by the input, but its unknown functional relationship is not encoded in $\mathcal Q$. The set $\mathcal P(\mathcal Q)$ therefore allows all couplings with the specified marginals, including randomized conditional residual laws. The upper and lower failure probability bounds are''')
paragraph(r'The true residual is a deterministic function of the input.', '')
old = r'''The analysis has two tasks:
\begin{enumerate}
  \item \textbf{Ambiguity set design and statistical calibration.} Construct a residual ambiguity set and establish its coverage guarantee under explicit sampling conditions.
  \item \textbf{Tractable reformulations.} Derive exact and computationally tractable reformulations of the infinite-dimensional optimization problems defining the failure probability bounds.
\end{enumerate}'''
new = r'''Section~\ref{sec-ambiguity-set} constructs the residual ambiguity set and establishes finite-sample coverage of the failure probability bounds. Section~\ref{sec-reformulation} then derives their Lagrangian duals, proves strong duality through a finite reformulation, and obtains closed-form expressions.'''
assert main.count(old) == 1
main = main.replace(old, new, 1)
changes.append('Section 2 roadmap')

# Section 3: discrepancy, band construction, calibration, and coverage transfer.
paragraph(r'Failure occurs when $\xi\le-\hat g(\bm X)$', r'''Failure occurs when $\xi\le-\hat g(\bm X)$, so the residual cumulative distribution function (CDF) gives the marginal mass at or below each failure threshold. We use the D\"umbgen--Wellner (DW) construction \citep{L.J23} to control empirical CDF deviations simultaneously over all thresholds, with tolerances that vary across probability levels.''')
paragraph(r'The test inputs are independent draws', r'''The test inputs are independent draws from $\mathbb P$ and are independent of $\mathcal D^{\mathrm{tr}}$. We fix $N^{\mathrm{te}}\ge1$ before sampling and use these data to calibrate the residual ambiguity set.''')
needle = '\\end{definition}\n\nWe calibrate'
replacement = r'''\end{definition}

The threshold $\theta$ controls the corrected likelihood discrepancy. Its CDF tolerances vary across probability levels and can be asymmetric about the empirical CDF. Statistical calibration assigns a confidence level to this set.

We calibrate'''
assert main.count(needle) == 1
main = main.replace(needle, replacement, 1)
paragraph(r'A quantile of this reference statistic determines', '')
paragraph(r'Proposition~\ref{proposition-01} applies to arbitrary residual', r'''Proposition~\ref{proposition-01} applies to arbitrary residual distributions, including laws with atoms or infinite moments. For fixed $\phi$ and $\psi$, the reference law depends only on $N^{\mathrm{te}}$, so $\theta_{N^{\mathrm{te}}}(\delta)$ can be calibrated offline. \citet{L.J23} describe finite-sample evaluation using uniform order-statistic boundary probabilities. A conservative upper bound on the quantile in \eqref{eq-dw-calibrated-threshold} preserves \eqref{eq-cdf-coverage}.''')
paragraph(r'Residual-law coverage gives simultaneous bounds', r'''The residual-law coverage in Proposition~\ref{proposition-01} transfers to the failure probability bounds defined in Section~\ref{sec-problem}.''')
theorem = main.index(r'\begin{theorem}[Finite-sample failure probability bounds]')
start = main.index(r'\begin{proof}', theorem)
end = main.index(r'\end{proof}', start) + len(r'\end{proof}')
main = main[:start] + r'''\begin{proof}
  On the event $\mathbb Q^\star\in\mathcal Q^{\mathrm{DW}}(\theta)$, the true joint distribution $\Pi^\star$ belongs to $\mathcal P\left(\mathcal Q^{\mathrm{DW}}(\theta)\right)$. Hence
  \[
    \underline p_{\hat f}\le p_{\hat f}(\Pi^\star)=p_f\le\overline p_{\hat f}.
  \]
  Proposition~\ref{proposition-01} assigns this event conditional probability at least $1-\delta$ given $\mathcal D^{\mathrm{tr}}$, proving \eqref{eq-failure-probability-coverage}.
\end{proof}''' + main[end:]
changes.append('Coverage-transfer proof: retain event inclusion and its probability once')
paragraph(r'The event $\mathbb Q^\star\in\mathcal Q^{\mathrm{DW}}(\theta)$ gives both', r'''The same event gives both inequalities, so $1-\delta$ is the confidence level for the entire interval. For fixed test data, $0\le\theta_1\le\theta_2$ implies $\mathcal Q^{\mathrm{DW}}(\theta_1)\subseteq\mathcal Q^{\mathrm{DW}}(\theta_2)$, making the lower bound nonincreasing and the upper bound nondecreasing in $\theta$. A higher prescribed confidence level requires a nondecreasing calibrated threshold and therefore gives a wider or unchanged interval.''')
paragraph(r'The interval accounts for finite-sample uncertainty', r'''The coverage argument also applies to any residual ambiguity set containing $\mathbb Q^\star$ with conditional probability at least $1-\delta$. It remains to evaluate the DW extrema in \eqref{eq-upper-bound} and \eqref{eq-lower-bound}.''')

# Section 4 retains its complete technical proofs and all existing displays.
paragraph(r'Scalar inversion turns the DW constraint', r'''Throughout this section, the training data, the test residuals, and $\theta\ge0$ are fixed. We first invert the DW constraint into linear rank restrictions, then derive the Lagrangian duals and prove their exactness through finite linear programs. The ordered constraints yield closed-form bounds. The main results use $\Xi=\mathbb R$; Remark~\ref{rem-interval-support} treats known interval support.''')
paragraph(r'The upper rank constraints limit mass strictly below', r'''The open upper and closed lower half-lines distinguish mass at the observed residuals. Each scalar acceptance interval can be computed by one-dimensional bisection.''')
paragraph(r'These candidate bounds hold for every admissible', r'''These threshold bounds will provide dual certificates; the finite reformulation will establish their sharpness.''')
paragraph(r'The marginal equality fixes the input law', r'''The marginal equalities fix the input law and total mass one. For $\Xi=\mathbb R$, the product of $\mathbb P$ and the empirical residual law is feasible for every $\theta\ge0$.''')
paragraph(r'The remaining supremum and infimum combine', r'''To evaluate the envelopes in Lemma~\ref{lem-weak-duality}, use the fact that the residual penalty changes only at observed residuals. For $\Xi=\mathbb R$, separating these values from the intervening intervals gives $J:=2K+1$ residual cells:''')
paragraph(r'The singleton cells retain residual atoms', r'''The singleton cells retain the distinction between the two rank events. The penalty is constant on each $\Xi_j$, with value''')
paragraph(r'For inputs in $\mathcal X_i$, residual cells with', r'''For inputs in $\mathcal X_i$, cells with $j\le2i$ always cause failure, and those with $j\ge2i+2$ are always safe. Only the overlapping interval $\Xi_{2i+1}$ gives different upper and lower coefficients. At threshold equality, the upper assignment may move mass to the left endpoint; the proof below establishes its feasibility. The cell weights and coefficients give the following finite duals.''')
paragraph(r'The finite LPs establish exactness of the duals.', r'''The ordered coefficients in \eqref{eq-cell-costs} also identify optimal dual certificates, reducing both LPs to scans over the observed residual levels.''')
paragraph(r'The upper bound combines residual mass below an observed', r'''The upper bound combines residual mass below an observed value with the probability that the surrogate threshold reaches it. The lower bound measures the overlap required by every admissible coupling. For $p_{\mathrm{tar}}\in(0,1)$, the upper bound is at most $p_{\mathrm{tar}}$ exactly when some rank satisfies $u_k+H\left(-\xi_{(k)}^{\mathrm{te}}\right)\le p_{\mathrm{tar}}$. Thus certification requires both residual-tail control and a sufficiently small surrogate threshold probability.''')
paragraph(r'For a known residual law, bounding the CDF', r'''With a known residual law, the coupling problem is the classical fixed-marginal sum problem studied by \citet{M82} and \citet{F.N.S87}. Here the residual law also varies within a calibrated DW band, and the open and closed rank constraints retain atoms.''')
paragraph(r'Dependence uncertainty can remain even with a known', r'''Dependence uncertainty can remain even with a known residual marginal. For equally likely surrogate responses $0$ and $2$ and equally likely residuals $-1$ and $1$, failure is the intersection of the response-$0$ and residual-$-1$ events. Its probability ranges from $0$ to $1/2$ over couplings, whereas independence gives $1/4$. Further marginal calibration alone does not resolve this dependence uncertainty.''')
paragraph(r'Finite calibration remains relevant in the rare-event', r'''After zero failures in $N^{\mathrm{te}}$ independent tests, the one-sided exact binomial upper limit is $1-\delta^{1/N^{\mathrm{te}}}\approx\log(1/\delta)/N^{\mathrm{te}}$ \citep{C.P34}. In the DW model, the simple case $K=1$ and $H\left(-\xi_{(1)}^{\mathrm{te}}\right)=0$ gives an upper bound $\beta_0(\theta)$ determined by the simultaneous-band calibration. Verified support can exclude otherwise unobserved failures: in Remark~\ref{rem-interval-support}, $H(-a)=0$ rules out failure.''')
paragraph(r'For fixed $\theta$, evaluation requires scalar', r'''Evaluation requires scalar DW inversion, sorting and counting the test residuals, and computing the $K$ values $H\left(-\xi_{(k)}^{\mathrm{te}}\right)$. The endpoint table depends only on $N^{\mathrm{te}}$ and $\theta$ and can be precomputed. Given this table and the surrogate CDF values, the two scans cost $O(K)$.''')
paragraph(r'For $\theta\ge\theta_{N^{\mathrm{te}}}(\delta)$, these exact bounds inherit', r'''For $\theta\ge\theta_{N^{\mathrm{te}}}(\delta)$, the exact expressions retain the coverage in Theorem~\ref{theorem-01}. If the surrogate CDF is evaluated by independent auxiliary simulation, simultaneous upper CDF bounds can replace $H\left(-\xi_{(k)}^{\mathrm{te}}\right)$ in the upper expression, and simultaneous lower CDF bounds can replace it in the lower expression. These auxiliary bounds must hold conditionally on the test data, with their error probability included in the overall confidence budget.''')

# Preserve the former complete narrative without changing the optional appendix or archives.
updated = main + marker + protected
archived_main = old_main[old_main.index(r'\section{Problem Description}'):]
archive = (
    '\n\n% BEGIN PRESERVED SECTIONS 2--4 BEFORE NARRATIVE REVISION (2026-11-24)\n'
    + ''.join('%' + line for line in archived_main.splitlines(keepends=True))
    + '% END PRESERVED SECTIONS 2--4 BEFORE NARRATIVE REVISION\n'
)
updated = updated.rstrip('\n') + archive
assert path.read_bytes() == original_bytes, 'Source changed during preparation.'
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))

def count_words(text):
    text = re.sub(r'\$.*?\$', '', text, flags=re.S)
    text = re.sub(r'\\begin\{(?:equation\*?|align\*?)\}.*?\\end\{(?:equation\*?|align\*?)\}', '', text, flags=re.S)
    return len(re.findall(r'[A-Za-z]+(?:-[A-Za-z]+)*', text))

report = {'backup': str(backup), 'edited_passages': len(changes), 'changes': changes,
          'previous_main_word_count_approx': count_words(old_main),
          'revised_main_word_count_approx': count_words(main)}
Path('tmp/sections_2_to_4_flow_edits.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({key: value for key, value in report.items() if key != 'changes'}, indent=2))
