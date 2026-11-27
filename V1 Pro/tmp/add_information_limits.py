from datetime import datetime
from pathlib import Path
import json
import shutil

root = Path.cwd()
path = root / 'manuscript.tex'
bibpath = root / 'reference.bib'
original_bytes = path.read_bytes()
bib_bytes = bibpath.read_bytes()
original = original_bytes.decode('utf-8').replace('\r\n', '\n')
active, archives = original.split(r'\end{document}', 1)
backup = root / 'backups' / ('information_limits_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir()
for name in ['manuscript.tex', 'manuscript.pdf', 'reference.bib']:
    shutil.copy2(root / name, backup / name)

old_paragraph = r'''The analysis has two tasks:
\begin{enumerate}
  \item \textbf{Ambiguity set design and statistical calibration.} Construct a residual ambiguity set and establish its coverage guarantee under explicit sampling conditions.
  \item \textbf{Tractable reformulations.} Derive exact and computationally tractable reformulations of the infinite-dimensional optimization problems defining the failure probability bounds.
\end{enumerate}'''
new_paragraph = r'''The true residual is a deterministic function of the input. The joint ambiguity set enlarges its unknown graph to all joint laws satisfying the marginal restrictions, including randomized conditional residual laws. This relaxation provides bounds from residual-marginal information without specifying an input--residual dependence model. Section~\ref{sec-information} explains how paired test observations can add constraints and tighten these bounds.

The analysis has three tasks:
\begin{enumerate}
  \item \textbf{Ambiguity set design and statistical calibration.} Construct a residual ambiguity set and establish its coverage guarantee under explicit sampling conditions.
  \item \textbf{Tractable reformulations.} Derive exact and computationally tractable reformulations of the infinite-dimensional optimization problems defining the failure probability bounds.
  \item \textbf{Information content and statistical limits.} Identify when the bounds certify small failure probabilities, distinguish sampling uncertainty from dependence uncertainty, and incorporate additional paired evidence.
\end{enumerate}'''
assert active.count(old_paragraph) == 1
active = active.replace(old_paragraph, new_paragraph, 1)

anchor = r'''The upper bound combines residual mass below an observed value with the probability that the surrogate threshold reaches that value. The lower bound measures overlap that every admissible dependence structure must retain.'''
positioning = r'''The upper bound combines residual mass below an observed value with the probability that the surrogate threshold reaches that value. The lower bound measures overlap that every admissible dependence structure must retain.

For a known residual law, bounding the CDF of $\hat g(\bm X)+\xi$ over all couplings is the classical fixed-marginal sum problem studied by \citet{M82} and \citet{F.N.S87}. Corollary~\ref{thm-closed-form-bounds} gives its finite-band counterpart: the residual law varies within a statistically calibrated DW band, and the open and closed rank constraints retain atoms. The finite LP proof establishes sharpness for this marginal information model. Paired observations can supply further joint constraints, as developed in Section~\ref{sec-information}.'''
assert active.count(anchor) == 1
active = active.replace(anchor, positioning, 1)

addition = r'''\section{Information Content and Statistical Limits}
\label{sec-information}

The closed-form expressions identify the information needed to certify a small failure probability. For $\Xi=\mathbb R$ and a prescribed target $p_{\mathrm{tar}}\in(0,1)$, Corollary~\ref{thm-closed-form-bounds} gives
\begin{equation}
  \overline p_{\hat f}\le p_{\mathrm{tar}}
  \quad\Longleftrightarrow\quad
  \text{there exists }k\in\{1,\ldots,K\}\text{ such that }
  u_k+H\left(-\xi_{(k)}^{\mathrm{te}}\right)\le p_{\mathrm{tar}}.
  \label{eq-target-certification}
\end{equation}
At that residual level, both the allowed lower-tail residual mass and the probability that the surrogate reaches the corresponding failure threshold must be small. A small mean squared residual alone does not ensure this condition. More generally, the upper bound is below one exactly when some $u_k+H\left(-\xi_{(k)}^{\mathrm{te}}\right)<1$, and the lower bound is positive exactly when some $l_k+H\left(-\xi_{(k)}^{\mathrm{te}}\right)>1$.

Finite evaluation budgets impose a separate statistical limit. A function can agree with a safe surrogate at every evaluated input and fail on a region that the evaluations miss. The following theorem states this obstruction for arbitrary sampling strategies, including surrogate construction and adaptive evaluation locations. Its budget $N^{\mathrm{tot}}$ counts all calls to $g$, including training and calibration, whereas $N^{\mathrm{te}}$ denotes the independent test sample used in the DW construction.

\begin{theorem}[Information limit for unrestricted limit-state functions]
  \label{thm-information-limit}
  Suppose $\mathbb P$ is nonatomic. A procedure accesses an unknown measurable $g$ only through at most $N^{\mathrm{tot}}\ge1$ point evaluations and returns an upper bound $\widehat p_{\mathrm U}\in[0,1]$. It may randomize, choose inputs adaptively, and fit surrogates. Assume that, for every measurable $g$,
  \[
    \Pr_g\left\{p_f(g)\le\widehat p_{\mathrm U}\right\}\ge1-\delta,
    \qquad p_f(g):=\mathbb P\{g(\bm X)\le0\},
  \]
  where $\Pr_g$ includes all sampling and internal randomization. On the safe function $g_0(\bm x)\equiv1$, every $\beta\in(\delta,1)$ satisfies
  \begin{equation}
    \Pr_{g_0}\left\{\widehat p_{\mathrm U}\ge
      1-\left(\frac{\delta}{\beta}\right)^{1/N^{\mathrm{tot}}}\right\}
      \ge1-\beta.
    \label{eq-information-limit}
  \end{equation}
  For fixed $\delta$ and $\beta$, the threshold is
  $\log(\beta/\delta)/N^{\mathrm{tot}}+O\left(\left(N^{\mathrm{tot}}\right)^{-2}\right)$.
  If the output on $g_0$ is constant, that constant is at least $1-\delta^{1/N^{\mathrm{tot}}}$.
\end{theorem}
\begin{proof}
  Fix $\varepsilon\in(0,1)$. Nonatomicity permits a partition of $\mathcal X$ into $L$ Borel cells of probability $1/L$. Choose uniformly a union $\mathcal V_L$ of $m_L:=\lceil\varepsilon L\rceil$ cells, and define $g_{\mathcal V_L}$ to be $-1$ on $\mathcal V_L$ and $1$ elsewhere. Every such function has failure probability $m_L/L\ge\varepsilon$.

  Fix the procedure's random seed and follow its evaluation path under $g_0$. This path visits at most $N^{\mathrm{tot}}$ distinct cells. For sufficiently large $L$, the probability over $\mathcal V_L$ of missing every visited cell is at least
  \[
    \frac{\binom{L-N^{\mathrm{tot}}}{m_L}}{\binom{L}{m_L}}
      \longrightarrow(1-\varepsilon)^{N^{\mathrm{tot}}}
      \qquad\text{as }L\to\infty.
  \]
  On this event, all evaluations, subsequent adaptive choices, and the output are identical under $g_0$ and $g_{\mathcal V_L}$. If the baseline output is below $\varepsilon$, it therefore fails to cover $p_f(g_{\mathcal V_L})$. Averaging over the uniformly chosen regions and the procedure's randomness, the assumed coverage for every $g_{\mathcal V_L}$ gives
  \[
    \delta\ge
    \Pr_{g_0}\left\{\widehat p_{\mathrm U}<\varepsilon\right\}
    \frac{\binom{L-N^{\mathrm{tot}}}{m_L}}{\binom{L}{m_L}}.
  \]
  Letting $L\to\infty$ yields
  $\Pr_{g_0}\left\{\widehat p_{\mathrm U}<\varepsilon\right\}
    \le\delta/(1-\varepsilon)^{N^{\mathrm{tot}}}$.
  Substituting $\varepsilon=1-(\delta/\beta)^{1/N^{\mathrm{tot}}}$ proves \eqref{eq-information-limit}. The expansion follows from the exponential series. For a constant baseline output below $1-\delta^{1/N^{\mathrm{tot}}}$, choosing $\varepsilon$ between these values makes the last inequality impossible.
\end{proof}

The theorem gives a probability statement about any uniformly valid procedure. It rules out a certificate that is $o\left(1/N^{\mathrm{tot}}\right)$ in probability even on the safe baseline. A familiar exact benchmark arises from independent testing. If a deterministic binomial upper confidence limit uses only the number of failures among $N^{\mathrm{te}}$ independent inputs, its zero-failure value must satisfy
\begin{equation}
  \widehat p_{\mathrm U}(0)\ge1-\delta^{1/N^{\mathrm{te}}}
    =\frac{\log(1/\delta)}{N^{\mathrm{te}}}
      +O\left(\left(N^{\mathrm{te}}\right)^{-2}\right).
  \label{eq-zero-failure-benchmark}
\end{equation}
Indeed, if the reported value were smaller, a failure probability between it and $1-\delta^{1/N^{\mathrm{te}}}$ would be missed with probability $(1-p_f)^{N^{\mathrm{te}}}>\delta$. The one-sided exact binomial limit attains equality \citep{C.P34}. The coefficient depends on the confidence level and the calibration procedure. For example, when $K=1$ and $H\left(-\xi_{(1)}^{\mathrm{te}}\right)=0$, the DW upper bound equals $u_1=\beta_0(\theta)$, whose size also reflects the multiscale correction and the calibrated threshold. The information limit alone does not determine this cutoff's coefficient or sample-size dependence.

Additional certified information changes the class of possible hidden failures. With known residual support $[a,b]$, Remark~\ref{rem-interval-support} gives $\overline p_{\hat f}\le H(-a)$. Thus $H(-a)\le p_{\mathrm{tar}}$ can certify the target directly, and $H(-a)=0$ certifies zero failure probability. Other verified restrictions on the residual function can exclude hidden alternatives as well. A known support interval helps when its location relative to the surrogate response rules out failures. On a finite input support, exhaustive evaluation also determines $p_f$ exactly; nonatomicity is essential to the oracle theorem.

Dependence uncertainty has a different source. If the surrogate response takes values $0$ and $2$ with equal probabilities, and the known residual marginal assigns probability $1/2$ to each of $-1$ and $1$, failure occurs exactly when the response is $0$ and the residual is $-1$. Couplings with these marginals allow failure probabilities from $0$ to $1/2$. Independence gives $1/4$, while different deterministic residual functions can attain either endpoint. This gap remains under a known residual marginal because the marginal model leaves the locations of errors unrestricted.

The paired test observations contain additional evidence through the true failure indicators. Define their count by
\[
  C_{\mathrm f}^{\mathrm{te}}
    :=\sum_{j=1}^{N^{\mathrm{te}}}\mathbf1_{\{g(\bm x_j^{\mathrm{te}})\le0\}}.
\]
Conditional on the training data, this count is binomial with parameters $N^{\mathrm{te}}$ and $p_f$. An exact binomial interval \citep{C.P34} therefore constrains the joint failure probability directly. The following combination retains a closed-form evaluation.

\begin{proposition}[Combining marginal and paired evidence]
  \label{prop-paired-evidence}
  Under the sampling conditions of Proposition~\ref{proposition-01}, choose $\delta_{\mathrm{DW}},\delta_{\mathrm{bin}}>0$ with $\delta_{\mathrm{DW}}+\delta_{\mathrm{bin}}\le\delta<1$, and calibrate $\theta\ge\theta_{N^{\mathrm{te}}}(\delta_{\mathrm{DW}})$. Let $[\underline p^{\mathrm{bin}},\overline p^{\mathrm{bin}}]$ be a binomial interval based on $C_{\mathrm f}^{\mathrm{te}}$ with conditional coverage at least $1-\delta_{\mathrm{bin}}$. When the intervals overlap, define
  \[
    \underline p_{\hat f}^{\mathrm{comb}}
      :=\max\left\{\underline p_{\hat f},\underline p^{\mathrm{bin}}\right\},
    \qquad
    \overline p_{\hat f}^{\mathrm{comb}}
      :=\min\left\{\overline p_{\hat f},\overline p^{\mathrm{bin}}\right\}.
  \]
  If they do not overlap, set the combined interval to $[0,1]$. Then
  \begin{equation}
    \Pr\left\{\underline p_{\hat f}^{\mathrm{comb}}\le p_f
      \le\overline p_{\hat f}^{\mathrm{comb}}
      \,\middle|\,\mathcal D^{\mathrm{tr}}\right\}
      \ge1-\delta_{\mathrm{DW}}-\delta_{\mathrm{bin}}\ge1-\delta.
    \label{eq-paired-evidence-coverage}
  \end{equation}
  Under the conditions of Corollary~\ref{thm-closed-form-bounds}, a nonempty combined interval gives the exact lower and upper failure probabilities over
  \[
    \left\{\Pi\in\mathcal P\left(\mathcal Q^{\mathrm{DW}}(\theta)\right):
      \underline p^{\mathrm{bin}}\le p_{\hat f}(\Pi)
      \le\overline p^{\mathrm{bin}}\right\}.
  \]
\end{proposition}
\begin{proof}
  Theorem~\ref{theorem-01} gives conditional coverage $1-\delta_{\mathrm{DW}}$ for the DW interval. The binomial interval has conditional coverage $1-\delta_{\mathrm{bin}}$. A union bound gives simultaneous coverage at least $1-\delta_{\mathrm{DW}}-\delta_{\mathrm{bin}}$, even though both intervals use the same test data. On this event their intersection is nonempty and contains $p_f$, proving \eqref{eq-paired-evidence-coverage}.

  For exactness, Proposition~\ref{prop-finite-rank-constraints} makes the joint ambiguity set convex, and Theorem~\ref{thm-finite-dual-reformulations} supplies joint laws attaining both original endpoints. Mixing these laws attains every intermediate failure probability because $p_{\hat f}(\Pi)$ is linear in $\Pi$. Adding the two binomial inequalities therefore intersects the attainable interval with $[\underline p^{\mathrm{bin}},\overline p^{\mathrm{bin}}]$, giving the stated endpoints.
\end{proof}

The combined interval is contained in each component interval whenever they overlap, with both components evaluated at their allocated error probabilities. The added joint constraints are linear, so the refinement remains within the measure LP framework. In this way, paired evidence can reduce a marginal coupling gap without assuming residual independence or a parametric error model.

More detailed paired information can be retained by fixing input strata before calibration and constructing a DW band for the residual law within each stratum. Applying the results to the conditional input laws and summing the bounds with the stratum probabilities gives simultaneous bounds when the stratum error budgets sum to at most $\delta$. Conditional on the stratum membership labels, the observations within each stratum are independent draws from its conditional input law, so the DW calibration remains valid for every positive stratum sample size. A stratum with no observations contributes its full probability to the upper bound and zero to the lower bound. The partition must be fixed from training data or other information independent of the calibration sample. In particular, the test-dependent rank cells in \eqref{eq-input-cells} require fresh calibration data or a calibration that accounts for their selection if used as statistical strata.

'''
anchor = r'\bibliographystyle{elsarticle-harv}'
assert active.count(anchor) == 1
active = active.replace(anchor, addition + '\n' + anchor, 1)

bib_addition = r'''
@article{M82,
  title = {Estimates for the Distribution Function of a Sum of Two Random Variables When the Marginal Distributions are Fixed},
  author = {Makarov, G. D.},
  year = {1982},
  journal = {Theory of Probability \& Its Applications},
  volume = {26},
  number = {4},
  pages = {803--806},
  doi = {10.1137/1126086}
}

@article{F.N.S87,
  title = {Best-Possible Bounds for the Distribution of a Sum---a Problem of {Kolmogorov}},
  author = {Frank, M. J. and Nelsen, R. B. and Schweizer, B.},
  year = {1987},
  journal = {Probability Theory and Related Fields},
  volume = {74},
  number = {2},
  pages = {199--211},
  doi = {10.1007/BF00569989}
}

@article{C.P34,
  title = {The Use of Confidence or Fiducial Limits Illustrated in the Case of the Binomial},
  author = {Clopper, C. J. and Pearson, E. S.},
  year = {1934},
  journal = {Biometrika},
  volume = {26},
  number = {4},
  pages = {404--413},
  doi = {10.1093/biomet/26.4.404}
}
'''
assert not any(('{' + key + ',') in bib_bytes.decode('utf-8') for key in ['M82', 'F.N.S87', 'C.P34'])
archive = (
    '\n\n% BEGIN PRESERVED ACTIVE MANUSCRIPT BEFORE INFORMATION-LIMIT EXTENSION (2026-11-24)\n'
    + ''.join('%' + line + '\n' for line in original.split(r'\end{document}', 1)[0].splitlines())
    + '% END PRESERVED ACTIVE MANUSCRIPT BEFORE INFORMATION-LIMIT EXTENSION\n'
)
updated = active + r'\end{document}' + archives + archive
assert path.read_bytes() == original_bytes, 'Source changed during preparation.'
assert bibpath.read_bytes() == bib_bytes, 'Bibliography changed during preparation.'
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))
updated_bib = bib_bytes.decode('utf-8').replace('\r\n', '\n').rstrip('\n') + '\n' + bib_addition
bibpath.write_bytes(updated_bib.replace('\n', '\r\n').encode('utf-8'))
(root / 'tmp/information_limits_backup.json').write_text(json.dumps({'backup': str(backup)}, indent=2), encoding='utf-8')
print(json.dumps({'backup': str(backup), 'added_section': 'Information Content and Statistical Limits',
                  'added_citations': ['M82', 'F.N.S87', 'C.P34']}, ensure_ascii=False))
