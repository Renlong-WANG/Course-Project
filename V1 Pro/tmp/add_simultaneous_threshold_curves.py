from datetime import datetime
from pathlib import Path
import json
import shutil

root = Path.cwd()
path = root / 'manuscript.tex'
original_bytes = path.read_bytes()
original = original_bytes.decode('utf-8').replace('\r\n', '\n')
marker = '% BEGIN OPTIONAL APPENDIX: INFORMATION CONTENT AND STATISTICAL LIMITS (COMMENTED OUT)'
main, protected = original.split(marker, 1)
backup = root / 'backups' / ('simultaneous_threshold_curves_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir()
for name in ['manuscript.tex', 'manuscript.pdf', 'reference.bib']:
    shutil.copy2(root / name, backup / name)

old = r'''Section~\ref{sec-ambiguity-set} constructs the residual ambiguity set and establishes finite-sample coverage of the failure probability bounds. Section~\ref{sec-reformulation} then derives their Lagrangian duals, proves strong duality through a finite reformulation, and obtains closed-form expressions.'''
new = r'''Section~\ref{sec-ambiguity-set} constructs the residual ambiguity set and establishes finite-sample coverage of the failure probability bounds, simultaneously across response thresholds. Section~\ref{sec-reformulation} then derives their Lagrangian duals, proves strong duality through a finite reformulation, and obtains closed-form expressions.'''
assert main.count(old) == 1
main = main.replace(old, new, 1)

corollary = r'''The same calibrated set can be reused across response thresholds.

\begin{corollary}[Simultaneous bounds across response thresholds]
  \label{cor-simultaneous-threshold-bounds}
  Under the conditions of Theorem~\ref{theorem-01}, let $\mathcal Q=\mathcal Q^{\mathrm{DW}}(\theta)$. For $c\in\mathbb R$, write $p_f(c):=\mathbb P\left\{g(\bm X)\le c\right\}$ and define
  \[
    p_{\hat f}(\Pi;c):=\int_{\mathcal X\times\Xi}
      \mathbf1_{\{\hat g(\bm x)+\xi\le c\}}\,\Pi(\mathrm d\bm x,\mathrm d\xi),
  \]
  with lower and upper bounds
  \[
    \underline p_{\hat f}(c):=\inf_{\Pi\in\mathcal P(\mathcal Q)}p_{\hat f}(\Pi;c),
    \qquad
    \overline p_{\hat f}(c):=\sup_{\Pi\in\mathcal P(\mathcal Q)}p_{\hat f}(\Pi;c).
  \]
  Then
  \begin{equation}
    \Pr\left\{\underline p_{\hat f}(c)\le p_f(c)\le\overline p_{\hat f}(c),
      \ \forall c\in\mathbb R\,\middle|\,\mathcal D^{\mathrm{tr}}\right\}\ge1-\delta.
    \label{eq-threshold-curve-coverage}
  \end{equation}
  At $c=0$, these definitions recover the original failure probability and its bounds.
\end{corollary}
\begin{proof}
  On $\mathbb Q^\star\in\mathcal Q^{\mathrm{DW}}(\theta)$, the true joint law $\Pi^\star$ belongs to the same set $\mathcal P(\mathcal Q)$ for every $c$. Consequently,
  \[
    \underline p_{\hat f}(c)\le p_{\hat f}(\Pi^\star;c)=p_f(c)
      \le\overline p_{\hat f}(c),\qquad\forall c\in\mathbb R.
  \]
  Both bound curves are nondecreasing. Monotonicity and the CDF limits of $p_f$ imply that any violation is detected at a rational threshold or an atom of $g(\bm X)$, a countable set. The simultaneous event is therefore measurable. Proposition~\ref{proposition-01} gives the common residual-coverage event conditional probability at least $1-\delta$, proving \eqref{eq-threshold-curve-coverage}.
\end{proof}

One calibration therefore covers the entire response-threshold curve, including thresholds selected after observing the test data, without an additional confidence allocation across $c$. Complementing the endpoints also bounds the strict exceedance probabilities $\mathbb P\left\{g(\bm X)>c\right\}$ simultaneously. Here $g$, $\hat g$, and the input law $\mathbb P$ remain fixed. Fragility curves formed by conditioning on different hazard intensities require coverage for the corresponding conditional residual laws.

'''
anchor = r'The coverage argument also applies to any residual ambiguity set containing'
assert main.count(anchor) == 1
main = main.replace(anchor, corollary + anchor, 1)

curves = r'''The same formulas give the response-threshold curves in Corollary~\ref{cor-simultaneous-threshold-bounds}. Replacing $g$ and $\hat g$ by $g-c$ and $\hat g-c$ leaves every residual, rank count, and endpoint $l_k,u_k$ unchanged. The surrogate CDF becomes $t\mapsto H(t+c)$, so Corollary~\ref{thm-closed-form-bounds} gives
\begin{align}
  \overline p_{\hat f}(c)
    &=\min\left\{1,\min_{k=1,\ldots,K}\left[u_k+H\left(c-\xi_{(k)}^{\mathrm{te}}\right)\right]\right\},
    \label{eq-threshold-closed-upper}\\
  \underline p_{\hat f}(c)
    &=\max\left\{0,\max_{k=1,\ldots,K}\left[l_k+H\left(c-\xi_{(k)}^{\mathrm{te}}\right)-1\right]\right\}.
    \label{eq-threshold-closed-lower}
\end{align}
These identities hold for every $c\in\mathbb R$ and $\theta\ge0$, including $\theta=0$. When $\theta\ge\theta_{N^{\mathrm{te}}}(\delta)$, their coverage is simultaneous by \eqref{eq-threshold-curve-coverage}. An extremizing coupling may depend on $c$; the common feasible true joint law supplies the simultaneous guarantee.

'''
anchor = r'The upper bound combines residual mass below an observed value'
assert main.count(anchor) == 1
main = main.replace(anchor, curves + anchor, 1)

old = r'''The upper bound combines residual mass below an observed value with the probability that the surrogate threshold reaches it. The lower bound measures the overlap required by every admissible coupling. For $p_{\mathrm{tar}}\in(0,1)$, the upper bound is at most $p_{\mathrm{tar}}$ exactly when some rank satisfies $u_k+H\left(-\xi_{(k)}^{\mathrm{te}}\right)\le p_{\mathrm{tar}}$. Both terms must therefore be small at the same residual level.'''
new = r'''The upper bound combines residual mass below an observed value with the probability that the surrogate threshold reaches it. The lower bound measures the overlap required by every admissible coupling. For $p_{\mathrm{tar}}\in(0,1)$, the upper curve satisfies $\overline p_{\hat f}(c)\le p_{\mathrm{tar}}$ exactly when some rank satisfies $u_k+H\left(c-\xi_{(k)}^{\mathrm{te}}\right)\le p_{\mathrm{tar}}$. Both terms must therefore be small at the same residual level.'''
assert main.count(old) == 1
main = main.replace(old, new, 1)

anchor = r'Including the support endpoints in this list retains their atoms and the corresponding changes in failure status.'
addition = anchor + r''' For a response threshold $c$, replace $H(-a)$, $H(-b)$, and $H\left(-\xi_{(k)}^{\mathrm{te}}\right)$ by $H(c-a)$, $H(c-b)$, and $H\left(c-\xi_{(k)}^{\mathrm{te}}\right)$, respectively.'''
assert main.count(anchor) == 1
main = main.replace(anchor, addition, 1)

main = main.replace('Given this table and the surrogate CDF values, the two scans cost $O(K)$.',
                    'Given this table and the surrogate CDF values, the two scans cost $O(K)$ at each response threshold.', 1)
old = r'''For $\theta\ge\theta_{N^{\mathrm{te}}}(\delta)$, the exact expressions retain the coverage in Theorem~\ref{theorem-01}. If the surrogate CDF is evaluated by independent auxiliary simulation, simultaneous upper CDF bounds can replace $H\left(-\xi_{(k)}^{\mathrm{te}}\right)$ in the upper expression, and simultaneous lower CDF bounds can replace it in the lower expression. These auxiliary bounds must hold conditionally on the test data, with their error probability included in the overall confidence budget.'''
new = r'''For $\theta\ge\theta_{N^{\mathrm{te}}}(\delta)$, the exact expressions retain the coverage in Theorem~\ref{theorem-01} and Corollary~\ref{cor-simultaneous-threshold-bounds}. If $H$ is evaluated by independent auxiliary simulation, upper CDF bounds can replace its values in the upper expression, and lower CDF bounds can replace them in the lower expression. For one fixed response threshold, simultaneous bounds at its $K$ evaluation points suffice. To retain coverage of the entire response-threshold curve, the auxiliary bounds must hold over all arguments of $H$. In either case, they must hold conditionally on the test data, with their error probability included in the overall confidence budget.'''
assert main.count(old) == 1
main = main.replace(old, new, 1)

updated = main + marker + protected
assert path.read_bytes() == original_bytes, 'Source changed during preparation.'
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))
report = {'backup': str(backup),
          'added_core_labels': ['cor-simultaneous-threshold-bounds', 'eq-threshold-curve-coverage',
                               'eq-threshold-closed-upper', 'eq-threshold-closed-lower']}
Path('tmp/simultaneous_threshold_curves_edits.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
