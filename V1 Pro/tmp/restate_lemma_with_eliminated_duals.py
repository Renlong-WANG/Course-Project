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
active, archives = original.split(r'\end{document}', 1)
lemma_start = active.index(r'\begin{lemma}[Finite-dimensional Lagrangian duals and weak duality]')
lemma_end = active.index(r'\end{lemma}', lemma_start) + len(r'\end{lemma}')
proof_start = active.index(r'\begin{proof}', lemma_end)
proof_end = active.index(r'\end{proof}', proof_start) + len(r'\end{proof}')
theorem_start = active.index(r'\begin{theorem}[Exact finite reformulations and strong duality]', proof_end)
previous = active[lemma_start:theorem_start]
lemma = active[lemma_start:lemma_end]
proof = active[proof_start:proof_end]

lp_start = lemma.index('  The upper and lower Lagrangian dual values are given by the finite LPs\n')
lp_equations_start = lemma.index(r'  \begin{equation}', lp_start)
lp_end = lemma.index('  Their optimal values satisfy', lp_equations_start)
lp_equations = lemma[lp_equations_start:lp_end]
reduced_label = proof.index(r'\label{eq-upper-measure-dual}')
reduced_start = proof.rfind(r'  \begin{align}', 0, reduced_label)
reduced_end = proof.index(r'  \end{align}', reduced_label) + len(r'  \end{align}')
reduced_equations = proof[reduced_start:reduced_end]
assert reduced_equations.count(r'&=\inf') == reduced_equations.count(r'&=\sup') == 1
reduced_statement = reduced_equations.replace(r'&=\inf', r'&:=\inf', 1).replace(r'&=\sup', r'&:=\sup', 1)
lemma = (lemma[:lp_start]
    + '  Eliminating the input marginal multiplier gives the upper and lower Lagrangian dual problems\n'
    + reduced_statement + '\n' + lemma[lp_end:])

lp_equations = lp_equations.replace(r':=\inf', r'=\inf', 1).replace(r':=\sup', r'=\sup', 1)
old_intro = ('  The envelopes are bounded and constant on the Borel cells $\\mathcal X_i$, so they belong to $\\mathcal F_{\\mathrm b}(\\mathcal X)$. '
             'They respectively minimize and maximize the expectation over feasible marginal functions. Substitution yields\n')
new_intro = ('  The envelopes are bounded and constant on the Borel cells $\\mathcal X_i$, so they belong to $\\mathcal F_{\\mathrm b}(\\mathcal X)$. '
             'They respectively minimize and maximize the expectation over feasible marginal functions. Substituting them into the functional dual objectives gives '
             '\\eqref{eq-upper-measure-dual} and \\eqref{eq-lower-measure-dual}. '
             'Introducing epigraph variables $z_i$ for the upper maxima and hypograph variables $z_i$ for the lower minima gives the equivalent LPs\n')
assert proof.count(old_intro) == 1
proof = proof[:reduced_start] + lp_equations.rstrip('\n') + proof[reduced_end:]
proof = proof.replace(old_intro, new_intro, 1)
old_epigraph = r'  Replacing each maximum by an epigraph variable $z_i$, and each minimum by a hypograph variable $z_i$, gives \eqref{eq-finite-upper-dual} and \eqref{eq-finite-lower-dual}. This remains exact when $\mathbb P(\mathcal X_i)=0$, since $z_i$ can still be chosen as the corresponding finite envelope.'
new_epigraph = r'  Each $z_i$ can be chosen as its corresponding finite envelope, including on input cells with $\mathbb P(\mathcal X_i)=0$. Thus introducing these variables preserves both optimal values.'
assert proof.count(old_epigraph) == 1
proof = proof.replace(old_epigraph, new_epigraph, 1)
new_afterword = r'''The duals in \eqref{eq-upper-measure-dual} and \eqref{eq-lower-measure-dual} involve $2K$ nonnegative rank multipliers. Their equivalent LP forms \eqref{eq-finite-upper-dual} and \eqref{eq-finite-lower-dual} add $K+1$ free variables $z_i$ and $(K+1)(2K+1)$ pairwise inequalities. The envelope identities establish these representations before strong duality is invoked.

'''
replacement = lemma + '\n' + proof + '\n\n' + new_afterword
updated_active = active[:lemma_start] + replacement + active[theorem_start:]
old_certificate = r'Finally, let $\bm e_k$ be the $k$th unit vector. Upper and lower dual certificates are respectively'
new_certificate = r'Finally, let $\bm e_k$ be the $k$th unit vector. Certificates for the upper and lower LPs \eqref{eq-finite-upper-dual} and \eqref{eq-finite-lower-dual} are respectively'
assert updated_active.count(old_certificate) == 1
updated_active = updated_active.replace(old_certificate, new_certificate, 1)

backup = root / 'backups' / ('lemma_eliminated_duals_20261125_' + datetime.now().strftime('%H%M%S'))
backup.mkdir(parents=True)
for name in ['manuscript.tex', 'manuscript.pdf', 'manuscript.aux']:
    if (root / name).exists():
        shutil.copy2(root / name, backup / name)
archive = ''.join('%' + line for line in previous.splitlines(keepends=True))
header = '% BEGIN PRESERVED LEMMA BEFORE ELIMINATED-DUAL STATEMENT (2026-11-25)\n'
updated = (updated_active + r'\end{document}' + archives).rstrip('\n') + '\n\n'
updated += header + archive + '% END PRESERVED LEMMA BEFORE ELIMINATED-DUAL STATEMENT\n'
assert path.read_bytes() == original_bytes
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))

def code(text):
    return '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0]
        for line in text.split(r'\end{document}', 1)[0].splitlines())

def equations(text):
    result = {}
    for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', code(text), re.S):
        body = match.group(2).replace(':=', '=')
        canonical = re.sub(r'\s+', '', re.sub(r'\\label\{[^}]+\}', '', body))
        for label in re.findall(r'\\label\{([^}]+)\}', body):
            result[label] = canonical
    return result

new_code = code(updated)
labels = re.findall(r'\\label\{([^}]+)\}', new_code)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', new_code)
report = {
    'backup': str(backup),
    'all_numbered_mathematical_expressions_preserved': equations(original) == equations(updated),
    'numbered_equation_count': len(equations(updated)),
    'prefix_before_lemma_unchanged': updated_active[:lemma_start] == active[:lemma_start],
    'outside_lemma_and_certificate_reference_unchanged': updated_active[updated_active.index(r'\begin{theorem}[Exact finite reformulations'):].replace(new_certificate, old_certificate, 1) == active[theorem_start:],
    'all_prior_comment_archives_preserved': archives in updated,
    'original_lemma_commented_exactly': ''.join(line[1:] for line in archive.splitlines(keepends=True)) == previous,
    'duplicate_labels': [label for label, count in collections.Counter(labels).items() if count > 1],
    'undefined_references': sorted(set(refs) - set(labels)),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', new_code),
    'lemma_start_line': updated_active[:lemma_start].count('\n') + 1,
}
Path('tmp/lemma_eliminated_dual_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
assert all(report[key] for key in ['all_numbered_mathematical_expressions_preserved', 'prefix_before_lemma_unchanged',
    'outside_lemma_and_certificate_reference_unchanged', 'all_prior_comment_archives_preserved', 'original_lemma_commented_exactly'])
assert not any(report[key] for key in ['duplicate_labels', 'undefined_references', 'manual_sized_delimiters'])
