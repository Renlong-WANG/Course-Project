"""Reorder Section 4 while retaining its finite-aggregation proof and archived source."""
from pathlib import Path
import json
import re

root = Path.cwd()
backup = root / 'backups/cell_structure_20261124_210727'
original_bytes = (backup / 'manuscript.tex').read_bytes()
assert (root / 'manuscript.tex').read_bytes() == original_bytes, 'Source changed after backup.'
original = original_bytes.decode('utf-8')
original_lf = original.replace('\r\n', '\n')
active, old_tail = original_lf.split(r'\end{document}', 1)
section_start = active.index(r'\section{Tractable Reformulation}')
section_end = active.index(r'\bibliographystyle', section_start)
old_section = active[section_start:section_end]

# Introduce the input cells when the surrogate CDF first becomes useful.
old_h_intro = ('To interpret the resulting probability bounds, define the CDF of the surrogate response by '
               '$H(t):=\\mathbb P\\left\\{\\hat g(\\bm X)\\le t\\right\\}$ for all $t\\in\\mathbb R$. ')
new_h_intro = r'''To interpret the resulting probability bounds, define the CDF of the surrogate response by $H(t):=\mathbb P\left\{\hat g(\bm X)\le t\right\}$ for all $t\in\mathbb R$. The ordered residual values classify inputs according to the location of the failure threshold $-\hat g(\bm x)$. Set $\xi_{(0)}^{\mathrm{te}}:=-\infty$ and $\xi_{(K+1)}^{\mathrm{te}}:=+\infty$, with $H(-\infty):=0$ and $H(+\infty):=1$, and define the input cells and their probability masses by
\begin{equation}
  \begin{aligned}
    \mathcal X_i&:=\left\{\bm x\in\mathcal X:
      \xi_{(i)}^{\mathrm{te}}\le-\hat g(\bm x)<\xi_{(i+1)}^{\mathrm{te}}\right\},\\
    w_i&:=\mathbb P(\mathcal X_i)
      =H\left(-\xi_{(i)}^{\mathrm{te}}\right)-H\left(-\xi_{(i+1)}^{\mathrm{te}}\right),
      \qquad i=0,\ldots,K.
  \end{aligned}
  \label{eq-input-cells}
\end{equation}
These $K+1$ cells form a disjoint partition of $\mathcal X$. Each nested threshold event is a union of consecutive input cells, so
\begin{equation}
  \mathbf1_{\{\hat g(\bm x)\le-\xi_{(k)}^{\mathrm{te}}\}}
    =\sum_{i=k}^K\mathbf1_{\mathcal X_i}(\bm x),
  \qquad
  H\left(-\xi_{(k)}^{\mathrm{te}}\right)=\sum_{i=k}^K w_i,
  \qquad k=1,\ldots,K.
  \label{eq-input-threshold-masses}
\end{equation}
The half-open convention assigns an input with $-\hat g(\bm x)=\xi_{(k)}^{\mathrm{te}}$ to $\mathcal X_k$. Thus these identities retain threshold equalities even when $H$ has atoms.

'''
assert active.count(old_h_intro) == 1
active = active.replace(old_h_intro, new_h_intro, 1)

# Move the step function forward and abbreviate repeated penalty sums in Lemma 1.
step_function = r'''For $\bm\lambda,\bm\gamma\in\mathbb R_+^K$, collect the rank penalties in the residual step function
\begin{equation}
  \zeta_{\bm\lambda,\bm\gamma}(\xi)
  :=\sum_{k=1}^K\lambda_k\mathbf1_{\{\xi<\xi_{(k)}^{\mathrm{te}}\}}
    -\sum_{k=1}^K\gamma_k\mathbf1_{\{\xi\le\xi_{(k)}^{\mathrm{te}}\}}.
  \label{eq-dual-step-function}
\end{equation}

'''
lemma_start = active.index(r'\begin{lemma}[Lagrangian dual problems and weak duality]')
post_lemma_start = active.index('The functional multiplier has now been eliminated', lemma_start)
lemma = active[lemma_start:post_lemma_start]

def flexible_latex(expression):
    return r'\s*'.join(re.escape(token) for token in re.findall(r'\\[A-Za-z]+|[^\s]', expression))

upper_penalty = (r'-\sum_{k=1}^K\lambda_k\mathbf1_{\{\xi<\xi_{(k)}^{\mathrm{te}}\}}'
                 r'+\sum_{k=1}^K\gamma_k\mathbf1_{\{\xi\le\xi_{(k)}^{\mathrm{te}}\}}')
lower_penalty = (r'+\sum_{k=1}^K\lambda_k\mathbf1_{\{\xi<\xi_{(k)}^{\mathrm{te}}\}}'
                 r'-\sum_{k=1}^K\gamma_k\mathbf1_{\{\xi\le\xi_{(k)}^{\mathrm{te}}\}}')
lemma, upper_replacements = re.subn(flexible_latex(upper_penalty), lambda _: r'-\zeta_{\bm\lambda,\bm\gamma}(\xi)', lemma)
lemma, lower_replacements = re.subn(flexible_latex(lower_penalty), lambda _: r'+\zeta_{\bm\lambda,\bm\gamma}(\xi)', lemma)
assert (upper_replacements, lower_replacements) == (4, 2)
old_roles = ('Let $\\bm\\lambda,\\bm\\gamma\\in\\mathbb R_+^K$ denote the Lagrange multipliers associated '
             'with the upper and lower rank constraints, respectively. The corresponding Lagrangian dual problems are given by')
new_roles = ('Let $\\bm\\lambda,\\bm\\gamma\\in\\mathbb R_+^K$ denote the Lagrange multipliers associated '
             'with the upper and lower rank constraints, respectively. The unrestricted multiplier for the input marginal equality '
             'is $\\eta\\in\\mathcal F_{\\mathrm b}(\\mathcal X)$, where $\\mathcal F_{\\mathrm b}(\\mathcal X)$ is the space '
             'of bounded Borel measurable real-valued functions. Eliminating $\\eta$ pointwise gives the Lagrangian dual problems')
assert old_roles in lemma
lemma = lemma.replace(old_roles, new_roles, 1)
proof_start = lemma.index(r'\begin{proof}') + len(r'\begin{proof}')
first_display = lemma.index(r'\begin{equation*}', proof_start)
lemma = lemma[:proof_start] + '\n  The input marginal equality is equivalent to\n  ' + lemma[first_display:]

# The residual cells now follow Lemma 1, with penalty values before failure coefficients.
finite_start = active.index(r'\begin{theorem}[Finite-dimensional duals and strong duality]', post_lemma_start)
residual_aggregation = r'''The residual supremum and infimum in Lemma~\ref{lem-weak-duality} combine the rank penalty with the failure indicator. We first make the penalty values explicit, then identify the failure coefficients associated with the input cells in \eqref{eq-input-cells}. For the default support $\Xi=\mathbb R$, partition the residual space into $J:=2K+1$ cells:
\begin{equation}
  \begin{aligned}
    \Xi_{2k}&:=\left\{\xi_{(k)}^{\mathrm{te}}\right\},
      &&k=1,\ldots,K,\\
    \Xi_{2k+1}&:=\left(\xi_{(k)}^{\mathrm{te}},\xi_{(k+1)}^{\mathrm{te}}\right),
      &&k=0,\ldots,K.
  \end{aligned}
  \label{eq-residual-cells}
\end{equation}
The two partitions satisfy
\begin{equation}
  \mathcal X=\bigsqcup_{i=0}^K\mathcal X_i,
  \qquad
  \Xi=\bigsqcup_{j=1}^J\Xi_j.
  \label{eq-space-partitions}
\end{equation}
The singleton residual cells retain atoms at the observed residuals and distinguish the open upper rank constraints from the closed lower rank constraints. The step function is constant on each $\Xi_j$, with value
\begin{equation}
  \zeta_j:=\sum_{k=1}^K\lambda_k\mathbf1_{\{j<2k\}}
    -\sum_{k=1}^K\gamma_k\mathbf1_{\{j\le2k\}},
    \qquad j=1,\ldots,J.
  \label{eq-dual-cell-values}
\end{equation}
For $(\bm x,\xi)\in\mathcal X_i\times\Xi_j$, the failure indicator satisfies
\begin{equation}
  \underline h_{ij}:=\mathbf1_{\{j\le2i\}}
  \le\mathbf1_{\{\xi\le-\hat g(\bm x)\}}
  \le\overline h_{ij}:=\mathbf1_{\{j\le2i+1\}}.
  \label{eq-cell-costs}
\end{equation}
Residual cells with $j\le2i$ always cause failure for inputs in $\mathcal X_i$, and those with $j\ge2i+2$ are always safe. Only the overlapping interval $\Xi_{2i+1}$ distinguishes the two coefficients. At $-\hat g(\bm x)=\xi_{(i)}^{\mathrm{te}}$, this open interval is safe; attaining the upper coefficient then requires moving its assigned mass to the left endpoint. The proof below handles this case explicitly and constructs joint laws attaining the assigned objective values while preserving every rank constraint. The coefficients $w_i$, $\zeta_j$, and $\underline h_{ij},\overline h_{ij}$ now give finite linear programs for the dual values.

'''
active = active[:lemma_start] + step_function + lemma + residual_aggregation + active[finite_start:]

# Use parent-space notation consistently in the active manuscript.
for old_symbol, new_symbol in [(r'\mathcal E', r'\Xi'), (r'\mathcal A', r'\mathcal X'), (r'\mathcal I', r'\Xi')]:
    active = active.replace(old_symbol, new_symbol)

old_matrix_intro = ('  Every feasible joint law induces a probability matrix $\\bm\\pi=(\\pi_{ij})$, '
                    'with $\\pi_{ij}:=\\Pi(\\mathcal X_i\\times \\Xi_j)$, in\n')
new_matrix_intro = r'''  Using the partitions in \eqref{eq-space-partitions}, associate each feasible joint law with its matrix of joint cell probabilities $\bm\pi=(\pi_{ij})$, where
  \begin{equation}
    \pi_{ij}:=\Pi(\mathcal X_i\times\Xi_j),
    \qquad i=0,\ldots,K,\quad j=1,\ldots,J.
    \label{eq-joint-cell-masses}
  \end{equation}
  The row sums are the fixed input cell probabilities, and the rank constraints bound cumulative column sums. Hence $\bm\pi\in\mathcal C_\theta$, where
'''
assert old_matrix_intro in active
active = active.replace(old_matrix_intro, new_matrix_intro, 1)
for before, after in [
    ('select a provisional residual category', 'select a provisional residual cell'),
    ('In the overlapping category', 'In the overlapping residual cell'),
    ('in the overlapping category', 'in the overlapping residual cell'),
    ('A group with', 'An input cell with'),
    ('between adjacent categories', 'between adjacent residual cells'),
    ('The nested residual categories', 'The ordered residual cells'),
]:
    active = active.replace(before, after)

old_support_end = 'If $a=b$, both bounds equal $H(-a)$.\n\\end{remark}'
new_support_end = ('If $a=b$, both bounds equal $H(-a)$. '
                   'For the resulting partition on $\\Xi=[a,b]$, intersect the singleton and open-interval residual cells '
                   'from the augmented threshold list with $\\Xi$ and omit empty cells. Including the support endpoints '
                   'in this list retains their atoms and the corresponding changes in failure status.\n\\end{remark}')
assert old_support_end in active
active = active.replace(old_support_end, new_support_end, 1)

# Preserve the preceding Section 4 as source comments, including all its proofs.
archive_header = '% BEGIN PRESERVED SECTION 4 BEFORE CELL-STRUCTURE REVISION (2026-11-24)\n'
archive_end = '% END PRESERVED SECTION 4 BEFORE CELL-STRUCTURE REVISION\n'
archive = ''.join('%' + line for line in old_section.splitlines(keepends=True))
updated = active + r'\end{document}' + old_tail
updated = updated.rstrip('\n') + '\n\n' + archive_header + archive + archive_end
(root / 'manuscript.tex').write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))

code = '\n'.join(line.split('%', 1)[0] for line in active.splitlines())
labels = re.findall(r'\\label\{([^}]+)\}', code)
references = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', code)
cites = {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', code) for key in group.split(',')}
bibkeys = set(re.findall(r'@\w+\{([^,]+),', (root / 'reference.bib').read_text(encoding='utf-8')))
role_order = [code.index(r'\label{' + label + '}') for label in [
    'eq-input-cells', 'eq-input-threshold-masses', 'eq-dual-step-function', 'lem-weak-duality',
    'eq-residual-cells', 'eq-dual-cell-values', 'eq-cell-costs', 'thm-finite-dual-reformulations', 'eq-joint-cell-masses']]
prefix_before_section = original_lf[:original_lf.index(r'\section{Tractable Reformulation}')]
report = {
    'requested_order_satisfied': role_order == sorted(role_order),
    'sections_1_to_3_only_support_symbol_changed': active[:active.index(r'\section{Tractable Reformulation}')]
        == prefix_before_section.replace(r'\mathcal E', r'\Xi'),
    'preexisting_comment_archive_unchanged': old_tail in updated,
    'prior_section_comment_archive_exact': ''.join(line[1:] for line in archive.splitlines(keepends=True)) == old_section,
    'bibliography_unchanged': (root / 'reference.bib').read_bytes() == (backup / 'reference.bib').read_bytes(),
    'upper_penalty_substitutions': upper_replacements,
    'lower_penalty_substitutions': lower_replacements,
    'old_support_and_cell_symbols_remaining': any(symbol in code for symbol in [r'\mathcal E', r'\mathcal A', r'\mathcal I']),
    'duplicate_labels': sorted({label for label in labels if labels.count(label) > 1}),
    'undefined_references': sorted(set(references) - set(labels)),
    'undefined_citations': sorted(cites - bibkeys),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', code),
    'unexpanded_joint_differential': bool(re.search(r'\\mathrm\s*d\s*\\Pi', code)),
}
(root / 'tmp/cell_structure_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
assert all(report[key] for key in ['requested_order_satisfied', 'sections_1_to_3_only_support_symbol_changed',
    'preexisting_comment_archive_unchanged', 'prior_section_comment_archive_exact', 'bibliography_unchanged'])
assert not any(report[key] for key in ['old_support_and_cell_symbols_remaining', 'duplicate_labels', 'undefined_references',
    'undefined_citations', 'manual_sized_delimiters', 'unexpanded_joint_differential'])
