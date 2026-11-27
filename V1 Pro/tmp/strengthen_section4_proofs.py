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
start = original.index(r'\section{Tractable Reformulation}')
end = original.index(r'\bibliographystyle', start)
old_section = original[start:end]
section = old_section
backup = root / 'backups' / ('section4_rigor_audit_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir()
for name in ['manuscript.tex', 'manuscript.pdf', 'reference.bib']:
    shutil.copy2(root / name, backup / name)

def prose(prefix, replacement):
    global section
    lines = section.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if line.lstrip().startswith(prefix)]
    assert len(matches) == 1, (prefix, len(matches))
    i = matches[0]
    indentation = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
    lines[i] = indentation + replacement.strip() + '\n'
    section = ''.join(lines)

# Scalar inversion: specify the interior index range, including K=1, and justify endpoint order.
needle = r'On $[\xi_{(k)}^{\mathrm{te}},\xi_{(k+1)}^{\mathrm{te}})$, the empirical CDF equals'
replacement = r'For $k=1,\ldots,K-1$, the empirical CDF on $\left[\xi_{(k)}^{\mathrm{te}},\xi_{(k+1)}^{\mathrm{te}}\right)$ equals'
assert section.count(needle) == 1
section = section.replace(needle, replacement, 1)
prose(r'With $p$ fixed, the corrected discrepancy', r'''With $p$ fixed, the corrected discrepancy decreases as $q$ approaches $p$ from either side. For empirical levels $q<q'$, an accepted value $p<q$ at level $q'$ remains accepted at level $q$; an accepted value $p>q'$ at level $q$ remains accepted at level $q'$. Since each acceptance interval contains its empirical level, these implications make both endpoints nondecreasing. The inequalities $\alpha_{c_k}(\theta)\le c_k/N^{\mathrm{te}}\le\beta_{c_k}(\theta)$ then give the stated compatibility conditions. This argument permits singleton intervals: at $\theta=0$, the interval for $q_j=1/2$ is $\{1/2\}$ because $\psi(1/2,p)=0$.''')

# Make the reversed Lagrangian signs and the lower pointwise constraint explicit.
prose('Reversing the inequality penalties for the lower problem', r'''For the lower problem, reversing the inequality penalties gives
  \begin{equation*}
    \mathcal L^-
    =-\bm\lambda^\top\bm u+\bm\gamma^\top\bm l
      +\mathbb E_{\mathbb P}\left[\eta(\bm X)\right]
      +\int_{\mathcal X\times\Xi}\left[
        \mathbf1_{\{\xi\le-\hat g(\bm x)\}}-\eta(\bm x)+\zeta_{\bm\lambda,\bm\gamma}(\xi)
      \right]\,\Pi(\mathrm d\bm x,\mathrm d\xi).
  \end{equation*}
  Its infimum over finite nonnegative measures is finite exactly when $\eta(\bm x)\le\mathbf1_{\{\xi\le-\hat g(\bm x)\}}+\zeta_{\bm\lambda,\bm\gamma}(\xi)$ for every $(\bm x,\xi)$. The pointwise largest feasible marginal function is therefore''')

# Give a fully defined measurable realization, including input atoms and null input cells.
prose('To establish the reverse inequalities, fix', r'''To establish the reverse inequalities, fix $\bm\pi\in\mathcal C_\theta$. Draw $\bm x$ from $\mathbb P$ and, on $\mathcal X_i$ with $w_i>0$, select a provisional residual cell $j$ with probability $\pi_{ij}/w_i$. These probabilities sum to one by the row equality. For $j\ne2i+1$, choose a fixed representative of $\Xi_j$; the two coefficients in \eqref{eq-cell-costs} then equal the actual failure indicator. The following assignments in the overlapping cell define the upper and lower joint laws $\Pi^+$ and $\Pi^-$, respectively.''')
lower_start = section.index('  For the lower problem, choose\n', section.index(r'\begin{theorem}[Finite-dimensional duals and strong duality]'))
finite_label = section.index(r'\label{eq-finite-primal-values}', lower_start)
finite_display = section.rfind(r'  \begin{equation}', lower_start, finite_label)
assert finite_display > lower_start
lower_realization = r'''  For the lower problem, assign $\xi=\left(\xi_{(i+1)}^{\mathrm{te}}-\hat g(\bm x)\right)/2$ when $i<K$, and $\xi=-\hat g(\bm x)+1$ when $i=K$. Each value lies in $\Xi_{2i+1}$ and strictly exceeds $-\hat g(\bm x)$, including when the threshold equals $\xi_{(i)}^{\mathrm{te}}$. This attains the lower coefficient and preserves the provisional residual cell.

  On an input cell with $w_i=0$, the row of $\bm\pi$ is zero; set $\xi=\xi_{(1)}^{\mathrm{te}}$ there. All residual assignments are Borel measurable functions of $\bm x$. Their finite mixtures define probability kernels, which, combined with $\mathbb P$, give joint probability laws with the prescribed input marginal. This construction also allows randomization at input atoms. Both joint laws satisfy the rank constraints and attain the assigned matrix objectives:
  \begin{equation*}
    p_{\hat f}(\Pi^+)=\sum_{i=0}^K\sum_{j=1}^J\overline h_{ij}\pi_{ij},
    \qquad
    p_{\hat f}(\Pi^-)=\sum_{i=0}^K\sum_{j=1}^J\underline h_{ij}\pi_{ij}.
  \end{equation*}
  Combining these identities with the initial bounds gives
'''
section = section[:lower_start] + lower_realization + section[finite_display:]
prose('The upper endpoint assignment can move mass', r'''The lower assignment retains every joint cell mass $\pi_{ij}$. The upper assignment can transfer mass from an open interval to its left endpoint while preserving the rank inequalities and the assigned objective value; equality of the resulting cell matrix with $\bm\pi$ is not needed for \eqref{eq-finite-primal-values}.''')
prose('The empirical product law gives a point', r'''For every $\theta\ge0$, a feasible matrix is induced by the empirical product law:
  \begin{equation*}
    \pi_{i,2k}^{\mathrm{emp}}:=w_i\frac{c_k-c_{k-1}}{N^{\mathrm{te}}},
    \qquad i=0,\ldots,K,\quad k=1,\ldots,K,
  \end{equation*}
  with all odd columns zero. Its open and closed rank probabilities are $c_{k-1}/N^{\mathrm{te}}$ and $c_k/N^{\mathrm{te}}$, respectively, so \eqref{eq-dw-counts-and-levels} makes it feasible also at $\theta=0$. The set $\mathcal C_\theta$ is closed, and its nonnegative entries sum to one, so it is compact. Both matrix objectives lie in $[0,1]$ and attain their optima, which the preceding constructions realize by joint laws. Finite LP strong duality therefore applies \citep[Section~5.2.3]{B.V04}. The row equalities have free multipliers $z_i$, and the rank inequalities have nonnegative multipliers $\lambda_k,\gamma_k$. Their dual constraints are $z_i+\zeta_j\ge\overline h_{ij}$ and $z_i-\zeta_j\le\underline h_{ij}$, giving \eqref{eq-finite-upper-dual} and \eqref{eq-finite-lower-dual}.''')
prose('Finite LP equality and Lemma~', r'''Finite LP equality and Lemma~\ref{lem-weak-duality} give \eqref{eq-strong-duality}. Optimal finite dual solutions supply optimal rank multipliers and marginal functions for the functional duals. Feasibility and finite optimal values suffice for this LP argument, including at $\theta=0$ when some rank inequalities can be binding for every feasible law.''')

# Complete the max-flow reduction and the normalization of suffix cuts.
needle = 'A partial flow can be completed to a transportation matrix using the remaining row and column masses, so the maximum flow equals the upper transport optimum.'
replacement = ('A transportation matrix restricts to a feasible flow on these permitted pairs. Conversely, a partial flow can be completed to a transportation matrix because the remaining row and column masses are nonnegative and have equal totals. Completion can only add permitted mass, so these two constructions identify the maximum flow with the upper transport optimum.')
assert section.count(needle) == 1
section = section.replace(needle, replacement, 1)
prose('For the lower problem, maximize safe mass', r'''For the lower problem, maximize safe mass on pairs $j>2i$ and subtract from one. The neighborhoods are nested suffixes. A finite minimum cut with a nonempty source-side row set can be normalized by including every row above its smallest index $k$ and retaining exactly the neighboring columns. For $k\ge1$, the cut has capacity''')
needle = 'Feasible column totals satisfy $Y_{2k-1}\\le u_k$ and $Y_{2k}\\ge l_k$. To attain all upper prefix bounds simultaneously, choose'
replacement = r'''The upper transport value is nondecreasing in the open prefixes $Y_{2k-1}$, and the lower transport value is nondecreasing in the closed prefixes $Y_{2k}$. Feasibility gives $Y_{2k-1}\le u_k$ and $Y_{2k}\ge l_k$. Thus maximizing the former and minimizing the latter give the claimed bounds if all relevant prefix limits can be attained simultaneously. For the upper prefixes, choose'''
assert section.count(needle) == 1
section = section.replace(needle, replacement, 1)

# Verify the pointwise envelope values at equality, not just the certificate inequalities.
prose('with objective $l_k+H', r'''with objective $l_k+H\left(-\xi_{(k)}^{\mathrm{te}}\right)-1$. The pointwise threshold inequalities give feasibility. For the upper envelope, when $-\hat g(\bm x)\ge\xi_{(k)}^{\mathrm{te}}$, choosing $\xi=\xi_{(k)}^{\mathrm{te}}$ attains value one. For the lower envelope, when $-\hat g(\bm x)<\xi_{(k)}^{\mathrm{te}}$, choosing $\xi\in\left(-\hat g(\bm x),\xi_{(k)}^{\mathrm{te}}\right]$ attains value minus one. In the complementary cases, a residual above both thresholds attains value zero. At threshold equality, the upper and lower envelopes are therefore one and zero, respectively. Inputs at equality are included in the closed CDF value $H\left(-\xi_{(k)}^{\mathrm{te}}\right)$. With zero rank multipliers, the marginal functions are the constants one and zero, giving the outer candidates.''')

# Preserve the entire preceding version in comments; leave all prior archives intact.
updated = original[:start] + section + original[end:]
header = '% BEGIN PRESERVED SECTION 4 BEFORE RIGOR AUDIT (2026-11-24)\n'
archive = ''.join('%' + line for line in old_section.splitlines(keepends=True))
updated = updated.rstrip('\n') + '\n\n' + header + archive + '% END PRESERVED SECTION 4 BEFORE RIGOR AUDIT\n'
assert path.read_bytes() == original_bytes, 'Source changed during the audit.'
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))

def numbered(source):
    result = {}
    for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', source, re.S):
        body = match.group(2)
        canonical = re.sub(r'\s+', '', re.sub(r'\\label\{[^}]+\}', '', body))
        for label in re.findall(r'\\label\{([^}]+)\}', body):
            result[label] = canonical
    return result

old_active = original.split(r'\end{document}', 1)[0]
active = updated.split(r'\end{document}', 1)[0]
code = '\n'.join(line.split('%', 1)[0] for line in active.splitlines())
labels = re.findall(r'\\label\{([^}]+)\}', code)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', code)
def cites(source):
    return {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', source) for key in group.split(',')}
bibkeys = set(re.findall(r'@\w+\{([^,]+),', (root / 'reference.bib').read_text(encoding='utf-8')))
report = {
    'backup': str(backup),
    'sections_1_to_3_unchanged': updated[:start] == original[:start],
    'all_29_numbered_formulas_and_labels_unchanged': numbered(old_active) == numbered(active) and len(numbered(active)) == 29,
    'prior_comment_archives_preserved': original[end:] in updated,
    'preaudit_section_archived_exactly': ''.join(line[1:] for line in archive.splitlines(keepends=True)) == old_section,
    'bibliography_byte_unchanged': (root / 'reference.bib').read_bytes() == (backup / 'reference.bib').read_bytes(),
    'citation_keys_preserved': cites(old_active) == cites(active),
    'duplicate_labels': [key for key, count in collections.Counter(labels).items() if count > 1],
    'undefined_references': sorted(set(refs) - set(labels)),
    'undefined_citations': sorted(cites(code) - bibkeys),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', code),
    'unexpanded_joint_differential': bool(re.search(r'\\mathrm\s*d\s*\\Pi', code)),
    'subsections_or_appendix': bool(re.search(r'\\(?:subsection|appendix)\b', code)),
}
(root / 'tmp/section4_rigor_source_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2, ensure_ascii=True))
assert all(report[key] for key in ['sections_1_to_3_unchanged', 'all_29_numbered_formulas_and_labels_unchanged',
    'prior_comment_archives_preserved', 'preaudit_section_archived_exactly', 'bibliography_byte_unchanged', 'citation_keys_preserved'])
assert not any(report[key] for key in ['duplicate_labels', 'undefined_references', 'undefined_citations',
    'manual_sized_delimiters', 'unexpanded_joint_differential', 'subsections_or_appendix'])
