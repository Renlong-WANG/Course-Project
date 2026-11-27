from datetime import datetime
from pathlib import Path
import json
import shutil

root = Path.cwd()
path = root / 'manuscript.tex'
original_bytes = path.read_bytes()
original = original_bytes.decode('utf-8').replace('\r\n', '\n')
active, archives = original.split(r'\end{document}', 1)
start = active.index(r'\section{Information Content and Statistical Limits}')
end = active.index(r'\bibliographystyle', start)
section = active[start:end]
backup = root / 'backups' / ('commented_information_appendix_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir()
for name in ['manuscript.tex', 'manuscript.pdf', 'reference.bib']:
    shutil.copy2(root / name, backup / name)

active = active[:start] + active[end:]
old = r'''The true residual is a deterministic function of the input. The joint ambiguity set enlarges its unknown graph to all joint laws satisfying the marginal restrictions, including randomized conditional residual laws. This relaxation provides bounds from residual-marginal information without specifying an input--residual dependence model. Section~\ref{sec-information} explains how paired test observations can add constraints and tighten these bounds.'''
new = r'''The true residual is a deterministic function of the input. The joint ambiguity set enlarges its unknown graph to all joint laws satisfying the marginal restrictions, including randomized conditional residual laws. This relaxation provides bounds from residual-marginal information without specifying an input--residual dependence model. Paired observations can refine the information model through additional joint constraints.'''
assert active.count(old) == 1
active = active.replace(old, new, 1)
active = active.replace('The analysis has three tasks:', 'The analysis has two tasks:', 1)
third_task = r'''  \item \textbf{Information content and statistical limits.} Identify when the bounds certify small failure probabilities, distinguish sampling uncertainty from dependence uncertainty, and incorporate additional paired evidence.
'''
assert active.count(third_task) == 1
active = active.replace(third_task, '', 1)

anchor = r'''The upper bound combines residual mass below an observed value with the probability that the surrogate threshold reaches that value. The lower bound measures overlap that every admissible dependence structure must retain.'''
explanation = anchor + r''' For a prescribed target $p_{\mathrm{tar}}\in(0,1)$, the upper bound certifies $p_f\le p_{\mathrm{tar}}$ exactly when at least one rank satisfies $u_k+H\left(-\xi_{(k)}^{\mathrm{te}}\right)\le p_{\mathrm{tar}}$. Both the allowed lower-tail residual mass and the surrogate threshold probability must therefore be small. A small mean squared residual alone does not ensure this condition.'''
assert active.count(anchor) == 1
active = active.replace(anchor, explanation, 1)

old = r'''For a known residual law, bounding the CDF of $\hat g(\bm X)+\xi$ over all couplings is the classical fixed-marginal sum problem studied by \citet{M82} and \citet{F.N.S87}. Corollary~\ref{thm-closed-form-bounds} gives its finite-band counterpart: the residual law varies within a statistically calibrated DW band, and the open and closed rank constraints retain atoms. The finite LP proof establishes sharpness for this marginal information model. Paired observations can supply further joint constraints, as developed in Section~\ref{sec-information}.'''
new = r'''For a known residual law, bounding the CDF of $\hat g(\bm X)+\xi$ over all couplings is the classical fixed-marginal sum problem studied by \citet{M82} and \citet{F.N.S87}. Corollary~\ref{thm-closed-form-bounds} gives its finite-band counterpart: the residual law varies within a statistically calibrated DW band, and the open and closed rank constraints retain atoms. The finite LP proof establishes sharpness for this marginal information model.

Dependence uncertainty can remain even with a known residual marginal. For equally likely surrogate responses $0$ and $2$ and equally likely residuals $-1$ and $1$, failure occurs exactly when the response is $0$ and the residual is $-1$. Couplings with these marginals allow failure probabilities from $0$ to $1/2$, whereas independence gives $1/4$. The marginal model leaves the locations of errors unrestricted; paired observations can supply additional constraints on their joint behavior.'''
assert active.count(old) == 1
active = active.replace(old, new, 1)

anchor = r'''For fixed $\theta$, evaluation requires scalar DW inversion, sorting and counting the test residuals, and computing the $K$ values $H\left(-\xi_{(k)}^{\mathrm{te}}\right)$.'''
benchmark = r'''Finite calibration remains relevant in the rare-event regime. After zero failures in $N^{\mathrm{te}}$ independent tests, the one-sided exact binomial upper limit is $1-\delta^{1/N^{\mathrm{te}}}\approx\log(1/\delta)/N^{\mathrm{te}}$ \citep{C.P34}. The DW cutoff also depends on its simultaneous-band calibration: when $K=1$ and $H\left(-\xi_{(1)}^{\mathrm{te}}\right)=0$, the upper bound is $\beta_0(\theta)$. Known support can provide information beyond the finite test sample. In Remark~\ref{rem-interval-support}, $H(-a)=0$ certifies zero failure probability because the residual lower bound rules out failure.

'''
assert active.count(anchor) == 1
active = active.replace(anchor, benchmark + anchor, 1)

header = '% BEGIN OPTIONAL APPENDIX: INFORMATION CONTENT AND STATISTICAL LIMITS (COMMENTED OUT)\n'
instructions = (
    '% This appendix is intentionally excluded from the compiled manuscript.\n'
    '% To enable it, uncomment the block below, including the appendix command.\n'
    '% It preserves the former Section 5, including all statements, proofs, and optional refinements.\n'
)
commented = ''.join('%' + line for line in (r'\appendix' + '\n' + section).splitlines(keepends=True))
block = header + instructions + commented + '% END OPTIONAL APPENDIX: INFORMATION CONTENT AND STATISTICAL LIMITS\n\n'
anchor = r'\bibliographystyle{elsarticle-harv}'
active = active.replace(anchor, block + anchor, 1)
updated = active + r'\end{document}' + archives
assert path.read_bytes() == original_bytes, 'Source changed during preparation.'
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))
Path('tmp/commented_appendix_backup.json').write_text(json.dumps({'backup': str(backup)}, indent=2), encoding='utf-8')
print(json.dumps({'backup': str(backup), 'main_sections': 4, 'optional_appendix_is_commented': True}))
