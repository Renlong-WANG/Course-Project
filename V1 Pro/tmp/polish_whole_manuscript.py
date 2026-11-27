from pathlib import Path
import collections
import json
import re

root = Path.cwd()
backup = root / 'backups/whole_tex_polish_20261124_212156'
original_bytes = (backup / 'manuscript.tex').read_bytes()
assert (root / 'manuscript.tex').read_bytes() == original_bytes, 'Source changed since backup; inspect before applying.'
original = original_bytes.decode('utf-8').replace('\r\n', '\n')
active, archive_tail = original.split(r'\end{document}', 1)
before = active
old_section = active[active.index(r'\section{Tractable Reformulation}'):active.index(r'\bibliographystyle')]

def prose(prefix, replacement):
    global active
    lines = active.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if line.lstrip().startswith(prefix)]
    assert len(matches) == 1, (prefix, len(matches))
    index = matches[0]
    indentation = lines[index][:len(lines[index]) - len(lines[index].lstrip())]
    lines[index] = indentation + replacement.strip() + '\n'
    active = ''.join(lines)

# Sections 2--3: preserve the model and sampling conditions while tightening the exposition.
prose(r'Evaluating $g$ at an input', r'''Evaluating $g$ can require an expensive high-fidelity simulation. We replace it with a computationally efficient surrogate trained on''')
prose(r'denote the training dataset used to construct', r'''to obtain a measurable predictor $\hat g:=\hat g_{\mathcal D^{\mathrm{tr}}}$. Model fitting and selection use only the training data and are completed before the test data are sampled. We condition on $\mathcal D^{\mathrm{tr}}$, treat $\hat g$ as fixed, and suppress this dependence in the notation.''')
prose(r'For a new input $\bm X', r'''For a new input $\bm X\sim\mathbb P$ independent of the training data, let $\mathbb Q^\star$ be the distribution of $\xi^\star:=\xi(\bm X)$. Let $\Xi\subseteq\mathbb R$ be a known Borel set with $\mathbb Q^\star(\Xi)=1$; the default choice is $\Xi=\mathbb R$. For any Borel set $\mathcal S$ in a Euclidean space, write $\mathcal B(\mathcal S)$ for its Borel sigma-algebra. Let $\mathcal M_+(\mathcal S)$ denote the finite nonnegative Borel measures concentrated on $\mathcal S$, and let $\mathcal M_1(\mathcal S)$ denote the probability measures.''')
prose(r'For a candidate residual distribution', r'''For a candidate residual law $\mathbb Q\in\mathcal M_1(\Xi)$, let $\Pi$ be a joint distribution on $\mathcal X\times\Xi$ with marginals $\Pi_{\bm X}=\mathbb P$ and $\Pi_\xi=\mathbb Q$. Its surrogate-based failure probability is''')
prose(r'The surrogate-based failure probability depends on both', r'''The failure probability depends on the residual law and its dependence on the input. Near the surrogate failure threshold, even a small residual can change the failure classification. We represent uncertainty in the residual law by an ambiguity set $\mathcal Q$ calibrated to contain $\mathbb Q^\star$ with high confidence. For a given $\mathcal Q$, define the joint ambiguity set''')
prose(r'The main tasks are therefore:', 'The analysis has two tasks:')
prose(r'In the surrogate formulation, failure occurs', r'''Failure occurs when $\xi\le-\hat g(\bm X)$, so the residual cumulative distribution function (CDF) determines the marginal mass below each failure threshold. Accurate tail control is needed for small failure probabilities. We use the D\"umbgen--Wellner (DW) construction \citep{L.J23} to control empirical CDF deviations simultaneously over all thresholds, with tolerances that vary across probability levels.''')
prose(r'We first introduce a local discrepancy', r'''Let $q$ and $p$ denote an empirical probability and a candidate probability. Following \citet{B.J79} and the CDF confidence bands of \citet{O95}, we measure their local discrepancy by the Bernoulli Kullback--Leibler divergence''')
prose(r'We fix the divergence parameter', r'''Before sampling, we fix the divergence parameter $s=1$, which gives \eqref{eq-bernoulli-kl}, and the correction parameter $\nu=1$. Set $\psi_0(v):=\rho(v)+\omega(v)$, with $\psi_0(0)=\psi_0(1)=+\infty$, and define the bivariate correction''')
prose(r'The functions $\rho$ and $\omega$', r'''The functions $\rho$ and $\omega$ vanish at $v=1/2$ and increase toward the probability boundaries. The minimum over the interval between $q$ and $p$ is therefore large only when both probabilities lie in the same tail. This correction balances fluctuations across probability scales in the simultaneous CDF constraint.''')
prose(r'We now construct the empirical CDF', 'Construct the empirical CDF from a test dataset')
prose(r'The test inputs $\bm x_1', r'''The test inputs are independent draws from $\mathbb P$ and are independent of $\mathcal D^{\mathrm{tr}}$. We fix $N^{\mathrm{te}}\ge1$ before sampling and use the test data to calibrate the residual ambiguity set, with the fitted surrogate held fixed.''')
prose(r'For $\mathbb Q\in\mathcal M_1(\Xi)$, write', r'''For $\mathbb Q\in\mathcal M_1(\Xi)$, write $F_{\mathbb Q}(t):=\mathbb Q\left(({-\infty},t]\right)$. At a threshold $t$, $q=\widehat F^{\mathrm{te}}(t)$ is the mean of the Bernoulli indicators in \eqref{eq-empirical-cdf}, and $p=F_{\mathbb Q}(t)$ is the candidate probability. Thus $N^{\mathrm{te}}\phi(q,p)$ is the Bernoulli log-likelihood difference between the empirical and candidate probabilities. Combining it with the multiscale correction gives $N^{\mathrm{te}}\phi(q,p)-\psi(q,p)$.''')
prose(r'The next proposition uses a quantile', 'A quantile of this reference statistic determines the calibration threshold.')
prose(r'Proposition~\ref{proposition-01} shows', r'''Proposition~\ref{proposition-01} applies to arbitrary residual distributions, including laws with atoms or infinite moments. With $\phi$ and $\psi$ fixed, the reference law depends only on $N^{\mathrm{te}}$. The threshold $\theta_{N^{\mathrm{te}}}(\delta)$ can therefore be calibrated offline for each confidence level $1-\delta$. \citet{L.J23} describe finite-sample evaluation using uniform order-statistic boundary probabilities. Any conservative upper bound on the quantile in \eqref{eq-dw-calibrated-threshold} preserves \eqref{eq-cdf-coverage}.''')
prose(r'The following theorem transfers the coverage guarantee', 'Residual-law coverage gives simultaneous bounds on the failure probability under the joint model.')

# State the coverage proof for the DW set; the generalization remains in the discussion.
prose(r'Consider an arbitrary, possibly data-dependent residual ambiguity set', r'''On the event $\mathbb Q^\star\in\mathcal Q^{\mathrm{DW}}(\theta)$, the true joint distribution $\Pi^\star$ belongs to $\mathcal P\left(\mathcal Q^{\mathrm{DW}}(\theta)\right)$. The definitions of the bounds and the identity $p_{\hat f}(\Pi^\star)=p_f$ give''')
theorem_proof_start = active.index(r'\begin{proof}', active.index(r'\begin{theorem}[Finite-sample failure probability bounds]'))
theorem_proof_end = active.index(r'\end{proof}', theorem_proof_start)
coverage_proof = active[theorem_proof_start:theorem_proof_end]
coverage_proof = coverage_proof.replace(r'\mathbb Q^\star\in\mathcal Q' + '\n', r'\mathbb Q^\star\in\mathcal Q^{\mathrm{DW}}(\theta)' + '\n')
active = active[:theorem_proof_start] + coverage_proof + active[theorem_proof_end:]
prose(r'In particular, taking $\mathcal Q=', r'''Proposition~\ref{proposition-01} bounds the right-hand side below by $1-\delta$, proving \eqref{eq-failure-probability-coverage}.''')
prose(r'The event $\mathbb Q^\star\in\mathcal Q^{\mathrm{DW}}(\theta)$ gives both', r'''The event $\mathbb Q^\star\in\mathcal Q^{\mathrm{DW}}(\theta)$ gives both inequalities, so $1-\delta$ is the confidence level for the entire interval. The threshold $\theta$ controls the corrected likelihood discrepancy; the resulting CDF tolerances vary with the probability level and can be asymmetric about the empirical CDF. For fixed test data, $0\le\theta_1\le\theta_2$ implies $\mathcal Q^{\mathrm{DW}}(\theta_1)\subseteq\mathcal Q^{\mathrm{DW}}(\theta_2)$. The lower failure bound is therefore nonincreasing in $\theta$, and the upper bound is nondecreasing. Increasing the prescribed confidence level gives a nondecreasing calibrated threshold and hence a wider or unchanged interval.

The interval accounts for finite-sample uncertainty in the residual law and uncertainty in its dependence on the input. Because the joint ambiguity set includes all couplings with the specified marginals, a gap can remain even when the residual marginal is known exactly. The same coverage argument applies to any residual ambiguity set containing $\mathbb Q^\star$ with conditional probability at least $1-\delta$ given $\mathcal D^{\mathrm{tr}}$.''')

# Section 4: retain the accepted order while making each transition serve the argument.
prose(r'The DW ambiguity set imposes a nonlinear constraint', r'''Scalar inversion turns the DW constraint into linear restrictions on residual probabilities. These restrictions lead to Lagrangian duals, exact finite linear programs, and closed-form failure probability bounds. Throughout this section, the training data, the test residuals, and $\theta\ge0$ are fixed. The main results use $\Xi=\mathbb R$; the final remark treats known interval support.''')
prose(r'Let $\xi_{(1)}^{\mathrm{te}}<', r'''Let $\xi_{(1)}^{\mathrm{te}}<\cdots<\xi_{(K)}^{\mathrm{te}}$ be the distinct ordered test residuals. Define''')
prose(r'Each acceptance set in \eqref{eq-dw-rank-acceptance}', r'''Each scalar acceptance set defined above is a nonempty closed interval containing $q_j$. Define''')
prose(r'For fixed $q$, the Bernoulli divergence increases', r'''For fixed $q$, the Bernoulli divergence increases as $p$ moves away from $q$, while $\psi(q,p)$ cannot increase as the interval between $q$ and $p$ expands. The corrected discrepancy therefore decreases toward $q$ from below and increases above $q$. It is continuous for $p\in(0,1)$ and equals $-\psi_0(q)\le0$ at $p=q$. The boundary conventions in Section~\ref{sec-ambiguity-set} give a nonempty closed acceptance interval also for $q\in\{0,1\}$. Scalar inversion at each empirical CDF level yields the stated CDF band, following \citet[Supplement, Section~S.6]{L.J23}.''')
prose(r'With $p$ fixed, the corrected discrepancy also', r'''With $p$ fixed, the corrected discrepancy decreases as $q$ approaches $p$ from below and increases above $p$. Since each acceptance interval contains $q$, both endpoints are nondecreasing in $q$. In particular, $\alpha_{c_k}(\theta)\le c_k/N^{\mathrm{te}}\le\beta_{c_k}(\theta)$, which gives the stated compatibility inequalities.''')
prose(r'The upper rank constraint limits residual mass', r'''The upper rank constraints limit mass strictly below each observed residual, while the lower constraints guarantee mass at or below it. The two half-lines retain possible atoms at the observed values. The scalar endpoints can be found by one-dimensional bisection, after which the ambiguity set is described by linear constraints on the residual law.''')

# Correct the input-probability typo and group the cells and weights in one unnumbered display.
input_start = active.index('To interpret the resulting probability bounds')
input_end = active.index('For every rank $k$', input_start)
input_block = r'''Define the surrogate-response CDF by $H(t):=\mathbb P\left\{\hat g(\bm X)\le t\right\}$ for $t\in\mathbb R$. The observed residuals classify inputs by the location of the failure threshold $-\hat g(\bm x)$. Set $\xi_{(0)}^{\mathrm{te}}:=-\infty$ and $\xi_{(K+1)}^{\mathrm{te}}:=+\infty$, with $H(-\infty):=0$ and $H(+\infty):=1$. The input cells and their probabilities are
\[
  \begin{aligned}
    \mathcal X_i&:=\left\{\bm x\in\mathcal X:
      \xi_{(i)}^{\mathrm{te}}\le-\hat g(\bm x)<\xi_{(i+1)}^{\mathrm{te}}\right\},\\
    w_i&:=\mathbb P(\mathcal X_i)
      =H\left(-\xi_{(i)}^{\mathrm{te}}\right)-H\left(-\xi_{(i+1)}^{\mathrm{te}}\right),
      \qquad i=0,\ldots,K.
  \end{aligned}
\]
These $K+1$ cells partition $\mathcal X$, and each threshold event is a union of consecutive cells:
\[
  \mathbf1_{\{\hat g(\bm x)\le-\xi_{(k)}^{\mathrm{te}}\}}
    =\sum_{i=k}^K\mathbf1_{\mathcal X_i}(\bm x),
  \qquad
  H\left(-\xi_{(k)}^{\mathrm{te}}\right)=\sum_{i=k}^K w_i,
  \qquad k=1,\ldots,K.
\]
The half-open convention assigns an input with $-\hat g(\bm x)=\xi_{(k)}^{\mathrm{te}}$ to $\mathcal X_k$, preserving threshold equalities even when $H$ has atoms.

'''
active = active[:input_start] + input_block + active[input_end:]
prose(r'The upper relation follows from a union of events:', r'''The upper inequality covers failure by a union of two events. The lower inequality guarantees failure on their intersection. Integrating under any feasible joint law gives''')
prose(r'These bounds require no independence assumption.', r'''These candidate bounds hold for every admissible dependence structure. The duality argument below establishes that the best candidate in each direction is exact.''')
prose(r'The lower problem minimizes the same integral', 'The lower problem minimizes the same integral subject to the same constraints:')
prose(r'The marginal equality fixes the input law', r'''The marginal equality fixes the input law and total mass one. The rank inequalities restrict the residual marginal while allowing its dependence on the input to vary. For every $\theta\ge0$, the product of $\mathbb P$ and the empirical residual law is feasible when $\Xi=\mathbb R$.''')
prose(r'Consider the feasible measure programs', r'''Consider the upper measure program \eqref{eq-measure-upper} and its lower minimization counterpart. Write $\bm u=(u_1,\ldots,u_K)^\top$ and $\bm l=(l_1,\ldots,l_K)^\top$. The nonnegative multipliers $\bm\lambda,\bm\gamma\in\mathbb R_+^K$ correspond to the upper and lower rank constraints. The input marginal equality has an unrestricted multiplier $\eta\in\mathcal F_{\mathrm b}(\mathcal X)$, the space of bounded Borel measurable real-valued functions. Eliminating $\eta$ pointwise gives the dual problems''')
prose(r'We first consider the upper measure program', r'''Relaxing the marginal equality and the rank inequalities gives the upper Lagrangian \citep[Section~5.1]{B.V04}''')
prose(r'Since $\Pi$ is no longer subject to a prescribed', r'''The relaxed measure has arbitrary finite nonnegative mass. If the integrand in the collected Lagrangian is positive at any point, scaling a point mass there by $M\to\infty$ gives $D^+=+\infty$. If the integrand is nonpositive everywhere, its supremum integral is zero, attained by the zero measure. The resulting functional dual is''')
prose(r'For fixed $\bm\lambda,\bm\gamma\in\mathbb R_+^K$, the pointwise smallest', r'''For fixed rank multipliers, the pointwise smallest feasible marginal function is''')
prose(r'This function is bounded in absolute value', r'''The envelope is bounded in absolute value by $1+\|\bm\lambda\|_1+\|\bm\gamma\|_1$. As a function of the real threshold replacing $-\hat g(\bm x)$, it is nondecreasing and hence Borel measurable. Composing it with the measurable surrogate gives $\eta^+_{\bm\lambda,\bm\gamma}\in\mathcal F_{\mathrm b}(\mathcal X)$. This smallest feasible function minimizes the expectation and yields the upper dual \eqref{eq-upper-measure-dual}.''')
prose(r'The derivation for the lower measure program', r'''Reversing the inequality penalties for the lower problem gives the pointwise largest feasible marginal function''')
prose(r'which also belongs to $\mathcal F_{\mathrm b}', r'''which is bounded and Borel measurable by the same argument. Substitution gives the lower dual \eqref{eq-lower-measure-dual}.''')
prose(r'Finally, by weak duality,', r'''For a primal feasible $\Pi$, the upper Lagrangian is at least $p_{\hat f}(\Pi)$ and the lower Lagrangian is at most $p_{\hat f}(\Pi)$. Every feasible upper dual solution therefore bounds the primal objective from above, and every feasible lower dual solution bounds it from below. Taking the respective optima and using the common nonempty primal feasible set gives \eqref{eq-weak-duality}.''')
prose(r'The residual supremum and infimum in Lemma', r'''The remaining supremum and infimum combine the residual penalty with the failure indicator. For $\Xi=\mathbb R$, the penalty changes only at observed residuals. Separate these values from the intervening intervals to form $J:=2K+1$ residual cells:''')
prose(r'The singleton residual cells retain atoms', r'''The singleton cells retain residual atoms and distinguish the strict upper rank inequalities from the nonstrict lower inequalities. The penalty is constant on each $\Xi_j$, with value''')
prose(r'Residual cells with $j\le2i$', r'''For inputs in $\mathcal X_i$, residual cells with $j\le2i$ always cause failure, and those with $j\ge2i+2$ are always safe. The overlapping interval $\Xi_{2i+1}$ determines the difference between the two coefficients. When $-\hat g(\bm x)=\xi_{(i)}^{\mathrm{te}}$, that interval is safe; the upper construction assigns its mass to the left endpoint. The proof below verifies this assignment. The weights $w_i$, penalty values $\zeta_j$, and failure coefficients now give finite linear programs for the duals.''')
prose(r'For $\Xi=\mathbb R$, $\mathcal Q=', r'''For $\Xi=\mathbb R$, $\mathcal Q=\mathcal Q^{\mathrm{DW}}(\theta)$, and every $\theta\ge0$, the dual values in Lemma~\ref{lem-weak-duality} equal the optimal values of''')
prose(r'Each finite LP has $3K+1$', r'''Each LP has $3K+1$ scalar variables and $(K+1)(2K+1)$ pairwise inequalities, together with multiplier nonnegativity. The free variables $z_i$ correspond to the input cell probability equalities. The finite LP optima and the corresponding measure primal and functional dual optima are attained.''')
prose(r'Using the partitions in \eqref{eq-space-partitions}', r'''For a feasible joint law, let $\bm\pi=(\pi_{ij})$ be its matrix of joint cell probabilities,''')
prose(r'The row sums are the fixed input cell probabilities', r'''Its row sums are the fixed input cell probabilities, and its cumulative column sums satisfy the rank constraints. Thus $\bm\pi\in\mathcal C_\theta$, where''')
prose(r'For the reverse inequalities, fix', r'''To establish the reverse inequalities, fix $\bm\pi\in\mathcal C_\theta$. Draw $\bm x$ from $\mathbb P$ and, on $\mathcal X_i$ with $w_i>0$, select a provisional residual cell $j$ with probability $\pi_{ij}/w_i$. For $j\ne2i+1$, choose a fixed representative of $\Xi_j$. Both coefficients in \eqref{eq-cell-costs} then equal the actual failure indicator.''')
prose(r'In the overlapping residual cell, choose', r'''For the upper problem, assign $\xi=-\hat g(\bm x)$ in the overlapping cell. This causes failure and lies in $\Xi_{2i+1}$ when $-\hat g(\bm x)>\xi_{(i)}^{\mathrm{te}}$. At equality, the assignment moves the provisional mass to the left endpoint. For $i\ge1$, any $\widetilde\xi\in\left(\xi_{(i)}^{\mathrm{te}},\xi_{(i+1)}^{\mathrm{te}}\right)$, and each observed threshold,''')
prose(r'Thus the move leaves all open upper probabilities', r'''The assignment leaves every open upper probability unchanged and can only increase the closed lower probabilities. It therefore preserves all rank constraints and attains the upper coefficient. For $i=0$, the finite threshold $-\hat g(\bm x)$ is strictly above $\xi_{(0)}^{\mathrm{te}}=-\infty$.''')
prose(r'The upper construction may redistribute mass', r'''The upper endpoint assignment can move mass between adjacent residual cells while preserving every rank constraint and the assigned objective value.''')
prose(r'The polytope is nonempty by empirical-product feasibility', r'''The polytope is nonempty by empirical-product feasibility and compact because its nonnegative entries sum to one. Both finite primal optima are attained, and the preceding constructions give optimal joint measures. Finite LP strong duality applies \citep[Section~5.2.3]{B.V04}. The row equalities have free multipliers $z_i$, and the rank inequalities have nonnegative multipliers $\lambda_k,\gamma_k$. Their dual constraints are $z_i+\zeta_j\ge\overline h_{ij}$ and $z_i-\zeta_j\le\underline h_{ij}$, giving \eqref{eq-finite-upper-dual} and \eqref{eq-finite-lower-dual}.''')
prose(r'Finally, an upper finite dual solution defines', r'''An upper finite dual solution defines a bounded Borel function $\eta(\bm x)=z_i$ on $\mathcal X_i$. The indicator bounds \eqref{eq-cell-costs} make it feasible for the functional upper dual, so $\eta^+_{\bm\lambda,\bm\gamma}(\bm x)\le z_i$. A lower finite dual solution similarly gives $\eta^-_{\bm\lambda,\bm\gamma}(\bm x)\ge z_i$. The reduced upper objective is therefore no greater than the finite upper dual objective, and the reduced lower objective is no smaller than the finite lower dual objective.

  Finite LP equality and Lemma~\ref{lem-weak-duality} give \eqref{eq-strong-duality}. Optimal finite dual solutions supply optimal rank multipliers and marginal functions for the functional duals. This argument uses feasibility and boundedness, so it includes $\theta=0$ and distributions with atoms.''')
prose(r'The theorem establishes an exact finite reformulation.', r'''The finite LPs establish exactness of the duals. Their ordered failure coefficients give a further simplification: the best single-threshold candidates derived above are already optimal.''')

# Keep the closed-form result and its optimal certificates within a single corollary.
active = active.replace(r'\begin{corollary}[Closed-form failure probability bounds]',
                        r'\begin{corollary}[Closed-form bounds and optimal certificates]', 1)
closed_start = active.index(r'\begin{corollary}[Closed-form bounds and optimal certificates]')
closed_end = active.index(r'\end{corollary}', closed_start)
active = active[:closed_end] + ('  Each dual optimum admits a certificate with at most one nonzero rank multiplier, of value one.\n') + active[closed_end:]
prose(r'There is a cut of capacity one.', r'''A cut of capacity one is available, so a minimum cut crosses no middle edge of capacity two. The row neighborhoods are nested prefixes. If the largest source-side row is $m<K$, including all smaller rows and retaining exactly their neighboring columns cannot increase the cut capacity. With $k=m+1$, this cut has capacity''')
prose(r'Monotonicity and \eqref{eq-rank-compatibility}', r'''Monotonicity and the compatibility conditions in Proposition~\ref{prop-finite-rank-constraints} make both allocations feasible. Substituting them into the upper and lower transport values above, then using \eqref{eq-finite-primal-values}, gives \eqref{eq-dw-closed-upper} and \eqref{eq-dw-closed-lower}.''')
prose(r'The closed forms also identify optimal rank multipliers', r'''Let $\bm e_k$ be the $k$th unit vector. An upper dual certificate is''')
prose(r'is feasible by \eqref{eq-upper-threshold-certificate}', r'''with objective $u_k+H\left(-\xi_{(k)}^{\mathrm{te}}\right)$. A lower dual certificate is''')
prose(r'is feasible by \eqref{eq-lower-threshold-certificate}', r'''with objective $l_k+H\left(-\xi_{(k)}^{\mathrm{te}}\right)-1$. The pointwise threshold inequalities derived above ensure feasibility. With zero rank multipliers, the optimal marginal functions are the constants one and zero, giving the outer candidates in the two closed forms.''')
prose(r'Selecting a minimizing upper candidate', r'''Choosing a minimizing candidate in \eqref{eq-dw-closed-upper} or a maximizing candidate in \eqref{eq-dw-closed-lower} gives an optimal full dual solution. Both families of rank constraints enter feasibility; their ordering permits an optimal certificate using at most one rank multiplier.''')
closed_proof = active.index(r'\begin{proof}', closed_start)
old_qed = active.index(r'\end{proof}', closed_proof)
certificate_start = active.index(r'Let $\bm e_k$ be the $k$th unit vector.', old_qed)
certificate_end = active.index(r'\begin{remark}[Known interval support]', certificate_start)
certificates = active[certificate_start:certificate_end].strip()
between = active[old_qed + len(r'\end{proof}'):certificate_start]
assert not between.strip()
interpretation = ('The upper bound combines residual mass below an observed value with the probability that the surrogate threshold reaches that value. '
                  'The lower bound measures overlap that every admissible dependence structure must retain.\n\n')
active = (active[:old_qed] + certificates + '\n' + r'\end{proof}' + '\n\n' + interpretation + active[certificate_end:])
prose(r'For a fixed $\theta$, evaluation consists', r'''For fixed $\theta$, evaluation requires scalar DW inversion, sorting and counting the test residuals, and computing the $K$ values $H\left(-\xi_{(k)}^{\mathrm{te}}\right)$. The endpoint table depends only on $N^{\mathrm{te}}$ and $\theta$ and can be precomputed. Given this table and the surrogate CDF values, the final upper and lower scans cost $O(K)$.''')

# Number only the principal definitions, optimization formulations, and results.
keep = {
    'eq-surrogate-failure-probability', 'eq-upper-bound', 'eq-lower-bound',
    'eq-bernoulli-kl', 'eq-empirical-cdf', 'eq-cdf-ambiguity-set',
    'eq-dw-reference-statistic', 'eq-dw-calibrated-threshold', 'eq-cdf-coverage',
    'eq-failure-probability-coverage', 'eq-finite-rank-constraints', 'eq-measure-upper',
    'eq-upper-measure-dual', 'eq-lower-measure-dual', 'eq-weak-duality',
    'eq-cell-costs', 'eq-finite-upper-dual', 'eq-finite-lower-dual', 'eq-strong-duality',
    'eq-cell-mass-polytope', 'eq-finite-primal-values', 'eq-dw-closed-upper', 'eq-dw-closed-lower',
}

# Remaining pointers to supporting formulas become descriptive mathematical references.
active = active.replace(r'\eqref{eq-rank-compatibility}',
                        r'the compatibility conditions in Proposition~\ref{prop-finite-rank-constraints}')
active = active.replace(r'\eqref{eq-space-partitions}', 'the input and residual partitions')
removed = []
display_re = re.compile(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', re.S)

def renumber(match):
    environment, body = match.groups()
    labels = re.findall(r'\\label\{([^}]+)\}', body)
    selected = [label for label in labels if label in keep]
    assert not selected or len(selected) == len(labels), ('mixed numbering', labels)
    if selected:
        return match.group(0)
    removed.extend(labels)
    body = re.sub(r'\n[ \t]*\\label\{[^}]+\}', '', body)
    return r'\begin{' + environment + '*}' + body + r'\end{' + environment + '*}'

active = display_re.sub(renumber, active)

# Remove obsolete labels from already-unnumbered displays and all remaining dangling references.
assert not any(r'\eqref{' + label + '}' in active for label in removed), [label for label in removed if r'\eqref{' + label + '}' in active]
assert r'\eqref{eq-input-cells}' not in active

# Normalize prose spacing only, leaving existing comments and previous versions intact.
active = re.sub(r'\n{4,}', '\n\n\n', active)
archive_header = '% BEGIN PRESERVED SECTION 4 BEFORE NUMBERING AND PROSE REVISION (2026-11-24)\n'
archive_end = '% END PRESERVED SECTION 4 BEFORE NUMBERING AND PROSE REVISION\n'
section_archive = ''.join('%' + line for line in old_section.splitlines(keepends=True))
updated = active + r'\end{document}' + archive_tail
updated = updated.rstrip('\n') + '\n\n' + archive_header + section_archive + archive_end
(root / 'manuscript.tex').write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))

# Verify core formulas independently of their prose, numbering, and placement.
def core_bodies(source):
    result = {}
    for match in display_re.finditer(source):
        body = match.group(2)
        labels = re.findall(r'\\label\{([^}]+)\}', body)
        canonical = re.sub(r'\\label\{[^}]+\}', '', body)
        canonical = re.sub(r'\s+', '', canonical)
        for label in labels:
            if label in keep:
                result[label] = canonical
    return result

old_core, new_core = core_bodies(before), core_bodies(active)
assert old_core == new_core and set(new_core) == keep

code = '\n'.join(line.split('%', 1)[0] for line in active.splitlines())
labels = re.findall(r'\\label\{([^}]+)\}', code)
references = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', code)
def citation_keys(source):
    return {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', source) for key in group.split(',')}
bib_keys = set(re.findall(r'@\w+\{([^,]+),', (root / 'reference.bib').read_text(encoding='utf-8')))
old_comments = [line for line in before.splitlines() if line.lstrip().startswith('%')]
new_comments = [line for line in active.splitlines() if line.lstrip().startswith('%')]
numbered_before = sum(len(re.findall(r'\\label\{eq-[^}]+\}', match.group(2))) or 1 for match in display_re.finditer(before))
report = {
    'numbered_equations_before': numbered_before,
    'numbered_equations_after': len(keep),
    'all_23_core_formulas_unchanged': old_core == new_core,
    'removed_auxiliary_equation_labels': removed,
    'duplicate_labels': [label for label, count in collections.Counter(labels).items() if count > 1],
    'undefined_references': sorted(set(references) - set(labels)),
    'undefined_citations': sorted(citation_keys(code) - bib_keys),
    'citation_keys_preserved': citation_keys(before) == citation_keys(active),
    'existing_active_comments_preserved': old_comments == new_comments,
    'preexisting_archive_preserved': archive_tail in updated,
    'prepolish_section_4_archived_exactly': ''.join(line[1:] for line in section_archive.splitlines(keepends=True)) == old_section,
    'bibliography_unchanged': (root / 'reference.bib').read_bytes() == (backup / 'reference.bib').read_bytes(),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', code),
    'unexpanded_joint_differential': bool(re.search(r'\\mathrm\s*d\s*\\Pi', code)),
    'old_support_or_cell_symbols': any(symbol in code for symbol in [r'\mathcal E', r'\mathcal A', r'\mathcal I']),
    'subsections_or_appendix': bool(re.search(r'\\(?:subsection|appendix)\b', code)),
    'input_probability_typo_corrected': r'\right)K.' not in code,
}
(root / 'tmp/whole_tex_polish_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
assert all(report[key] for key in ['all_23_core_formulas_unchanged', 'citation_keys_preserved', 'existing_active_comments_preserved',
    'preexisting_archive_preserved', 'prepolish_section_4_archived_exactly', 'bibliography_unchanged', 'input_probability_typo_corrected'])
assert not any(report[key] for key in ['duplicate_labels', 'undefined_references', 'undefined_citations', 'manual_sized_delimiters',
    'unexpanded_joint_differential', 'old_support_or_cell_symbols', 'subsections_or_appendix'])
