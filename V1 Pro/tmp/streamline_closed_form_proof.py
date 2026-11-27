from pathlib import Path
import json
import re

path = Path('manuscript.tex')
original_bytes = path.read_bytes()
original = original_bytes.decode('utf-8').replace('\r\n', '\n')
active, archives = original.split(r'\end{document}', 1)
active = active.replace(
    r'This argument permits singleton intervals: at $\theta=0$, the interval for $q_j=1/2$ is $\{1/2\}$ because $\psi(1/2,p)=0$.',
    r'This argument permits singleton intervals: if $q_j=1/2$ and $\theta=0$, the acceptance interval is $\{1/2\}$ because $\psi(1/2,p)=0$.',
    1,
)
active = active.replace(
    r'Consider the upper measure program \eqref{eq-measure-upper} and its lower minimization counterpart.',
    r'Consider the feasible upper measure program \eqref{eq-measure-upper} and its lower minimization counterpart.',
    1,
)
corollary = active.index(r'\begin{corollary}[Closed-form bounds and optimal certificates]')
start = active.index(r'\begin{proof}', corollary)
end = active.index(r'\end{proof}', start) + len(r'\end{proof}')
previous = active[start:end]
replacement = r'''\begin{proof}
  Fix nonnegative column masses $\bm y=(y_1,\ldots,y_J)^\top$ with $\sum_j y_j=1$, and write $Y_j:=\sum_{r=1}^j y_r$. Let $\mathcal T(\bm w,\bm y)$ contain the transportation matrices with row sums $\bm w=(w_0,\ldots,w_K)^\top$ and column sums $\bm y$. It contains the product matrix $\pi_{ij}=w_i y_j$. The rank constraints depend only on $\bm y$, through $Y_{2k-1}\le u_k$ and $Y_{2k}\ge l_k$.

  For fixed $\bm y$, the upper problem maximizes mass on failure pairs $j\le2i+1$; the lower problem maximizes mass on safe pairs $j>2i$ and subtracts it from one. Both are maximum-flow problems: source-to-row capacities are $w_i$, column-to-sink capacities are $y_j$, and a row is connected to each permitted column by an edge of capacity two. Restricting a transportation matrix to permitted pairs gives a feasible flow. Conversely, any flow can be completed to a transportation matrix because the remaining row and column masses are nonnegative and have equal totals. These two operations show that the maximum flow equals the maximum permitted mass.

  A cut of capacity one is available, so a minimum cut crosses no edge of capacity two. Its source-side columns can be taken to be exactly the neighbors of its source-side rows. Because the neighborhoods are nested, adding any row whose neighbors are already included cannot increase the cut capacity. Thus, apart from empty or full row sets, upper-problem cuts reduce to the rows $i<k$ and columns $j<2k$, while safe-mass cuts reduce to the rows $i\ge k$ and columns $j>2k$. For $k=1,\ldots,K$, their capacities are, respectively,
  \begin{align*}
    \sum_{i=k}^K w_i+Y_{2k-1}
      &=H\left(-\xi_{(k)}^{\mathrm{te}}\right)+Y_{2k-1},\\
    \sum_{i=0}^{k-1}w_i+1-Y_{2k}
      &=2-H\left(-\xi_{(k)}^{\mathrm{te}}\right)-Y_{2k}.
  \end{align*}
  Empty and full row sets give capacity one. Each remaining cut therefore tests a single separation between ordered cells. The max-flow/min-cut theorem \citep{F.F56} gives
  \begin{align*}
    \max_{\bm\pi\in\mathcal T(\bm w,\bm y)}\sum_{i,j}\overline h_{ij}\pi_{ij}
      &=\min\left\{1,\min_k\left[H\left(-\xi_{(k)}^{\mathrm{te}}\right)+Y_{2k-1}\right]\right\},\\
    \min_{\bm\pi\in\mathcal T(\bm w,\bm y)}\sum_{i,j}\underline h_{ij}\pi_{ij}
      &=\max\left\{0,\max_k\left[H\left(-\xi_{(k)}^{\mathrm{te}}\right)+Y_{2k}-1\right]\right\}.
  \end{align*}

  The first value is nondecreasing in every open prefix $Y_{2k-1}$, and the second is nondecreasing in every closed prefix $Y_{2k}$. It remains to attain all upper prefix limits simultaneously for the maximization, and all lower prefix limits simultaneously for the minimization. With $u_{K+1}=1$ and $l_0=0$, choose
  \begin{align*}
    &y_1^+:=u_1,\qquad y_{2k}^+:=u_{k+1}-u_k,\qquad
      y_{2k+1}^+:=0,\quad k=1,\ldots,K,\\
    &y_{2k-1}^-:=0,\qquad y_{2k}^-:=l_k-l_{k-1},\quad k=1,\ldots,K,
      \qquad y_J^-:=1-l_K.
  \end{align*}
  The monotonicity and compatibility conditions in Proposition~\ref{prop-finite-rank-constraints} make both vectors nonnegative with total mass one. Their prefixes satisfy
  \[
    Y_{2k-1}^+=u_k,\qquad Y_{2k}^+=u_{k+1}\ge l_k,
    \qquad Y_{2k}^-=l_k,\qquad Y_{2k-1}^-=l_{k-1}\le u_k.
  \]
  Hence both allocations are feasible and attain the required prefix limits. Substituting them into the fixed-column values and using \eqref{eq-finite-primal-values} proves \eqref{eq-dw-closed-upper} and \eqref{eq-dw-closed-lower}. Zero masses and coincident prefix limits are allowed, so this argument includes $\theta=0$.

  Finally, let $\bm e_k$ be the $k$th unit vector. The upper and lower dual certificates are, respectively,
  \begin{align*}
    &\bm\lambda=\bm e_k,\qquad \bm\gamma=\bm 0,\qquad
      \eta^+_{\bm e_k,\bm 0}(\bm x)
      =\mathbf1_{\{\hat g(\bm x)\le-\xi_{(k)}^{\mathrm{te}}\}},\\
    &\bm\lambda=\bm 0,\qquad \bm\gamma=\bm e_k,\qquad
      \eta^-_{\bm 0,\bm e_k}(\bm x)
      =\mathbf1_{\{\hat g(\bm x)\le-\xi_{(k)}^{\mathrm{te}}\}}-1.
  \end{align*}
  The threshold indicator inequalities established before Lemma~\ref{lem-weak-duality} give feasibility. To verify the envelope values, take $\xi=\xi_{(k)}^{\mathrm{te}}$ in the upper problem when $-\hat g(\bm x)\ge\xi_{(k)}^{\mathrm{te}}$, and $\xi\in\left(-\hat g(\bm x),\xi_{(k)}^{\mathrm{te}}\right]$ in the lower problem when $-\hat g(\bm x)<\xi_{(k)}^{\mathrm{te}}$. These choices attain one and minus one, respectively; a residual above both thresholds attains zero in the complementary cases. At threshold equality, the upper and lower envelopes are therefore one and zero, and the input is included in $H\left(-\xi_{(k)}^{\mathrm{te}}\right)$. The certificate objectives are exactly the inner candidates in \eqref{eq-dw-closed-upper} and \eqref{eq-dw-closed-lower}. Zero rank multipliers give the constant marginal functions one and zero, attaining the outer candidates. Selecting the best candidate thus supplies an optimal full dual solution with at most one nonzero rank multiplier.
\end{proof}'''
active = active[:start] + replacement + active[end:]
archive = (
    '\n\n% BEGIN PRESERVED CLOSED-FORM PROOF BEFORE STRUCTURAL REFINEMENT (2026-11-24)\n'
    + ''.join('%' + line + '\n' for line in previous.splitlines())
    + '% END PRESERVED CLOSED-FORM PROOF BEFORE STRUCTURAL REFINEMENT\n'
)
updated = active + r'\end{document}' + archives + archive
assert path.read_bytes() == original_bytes
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))
def word_count(text):
    return len(re.findall(r'[A-Za-z]+(?:-[A-Za-z]+)*', re.sub(r'\$.*?\$', '', text, flags=re.S)))
print(json.dumps({'previous_proof_words_approx': word_count(previous),
                  'revised_proof_words_approx': word_count(replacement),
                  'previous_proof_preserved_in_comments': True}))
