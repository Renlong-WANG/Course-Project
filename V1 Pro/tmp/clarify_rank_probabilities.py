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
start = active.index('The singleton cells distinguish probability strictly below an observed residual')
prop_start = active.index(r'\begin{proposition}[CDF band and residual cell probabilities]', start)
prop_end = active.index(r'\end{proof}', prop_start) + len(r'\end{proof}')
previous_fragment = active[start:prop_end]
previous_prop = active[prop_start:prop_end]
eq_start = previous_prop.index(r'  \begin{equation}')
eq_end = previous_prop.index(r'  \end{equation}', eq_start) + len(r'  \end{equation}')
finite_representation = previous_prop[eq_start:eq_end]
ordering_start = previous_prop.index('  The sequences $l_k$ and $u_k$')
ordering_end = previous_prop.index(r'\end{proposition}', ordering_start)
ordering = previous_prop[ordering_start:ordering_end]
proof_start = previous_prop.index(r'\begin{proof}')
proof = previous_prop[proof_start:]
old_sentence = r'Scalar inversion at each empirical CDF level yields the stated CDF band, following \citet[Supplement, Section~S.6]{L.J23}.'
new_sentence = r'''Scalar inversion of the DW constraint therefore gives the CDF band \citep[Supplement, Section~S.6]{L.J23}
  \[
    \alpha_{N^{\mathrm{te}}\widehat F^{\mathrm{te}}(t)}(\theta)
      \le F_{\mathbb Q}(t)
      \le\beta_{N^{\mathrm{te}}\widehat F^{\mathrm{te}}(t)}(\theta),
    \qquad\forall t\in\mathbb R.
  \]'''
assert proof.count(old_sentence) == 1
proof = proof.replace(old_sentence, new_sentence, 1)
repeat_start = proof.index('The residual partition gives\n')
repeat_end = proof.index('proving \\eqref{eq-finite-rank-constraints} and its half-line representation.', repeat_start)
repeat_end += len('proving \\eqref{eq-finite-rank-constraints} and its half-line representation.')
proof = proof[:repeat_start] + r'The rank-probability identities above then yield \eqref{eq-finite-rank-constraints}.' + proof[repeat_end:]
new_prop = (
    r'\begin{proposition}[Finite representation of the DW ambiguity set]' + '\n'
    + r'  \label{prop-finite-rank-constraints}' + '\n'
    + r'  Each acceptance set in \eqref{eq-dw-rank-acceptance} is a nonempty closed interval containing $q_j$. The DW ambiguity set has the finite representation' + '\n'
    + finite_representation + '\n' + ordering
    + r'\end{proposition}' + '\n' + proof
)
new_intro = r'''For any candidate residual law $\mathbb Q\in\mathcal M_1(\Xi)$, the open rank probability measures mass strictly below an observed residual, while the closed rank probability also includes mass at that value. For $k=1,\ldots,K$, the partition gives
\[
  \begin{aligned}
    \mathbb Q\left\{\xi<\xi_{(k)}^{\mathrm{te}}\right\}
      &=F_{\mathbb Q}\left(\xi_{(k)}^{\mathrm{te}}-\right)
        =\sum_{j<2k}\mathbb Q(\Xi_j),\\
    \mathbb Q\left\{\xi\le\xi_{(k)}^{\mathrm{te}}\right\}
      &=F_{\mathbb Q}\left(\xi_{(k)}^{\mathrm{te}}\right)
        =\sum_{j\le2k}\mathbb Q(\Xi_j).
  \end{aligned}
\]
Here $F_{\mathbb Q}(t-):=\lim_{s\uparrow t}F_{\mathbb Q}(s)$ is the CDF left limit. The two probabilities differ by the atom mass $\mathbb Q(\Xi_{2k})$.
'''
intro_end = active.index('\n\nDefine the surrogate-response CDF', start)
revised_fragment = new_intro + active[intro_end:prop_start] + new_prop
updated_active = active[:start] + revised_fragment + active[prop_end:]
backup = root / 'backups' / ('rank_probability_exposition_20261125_' + datetime.now().strftime('%H%M%S'))
backup.mkdir(parents=True)
for name in ['manuscript.tex', 'manuscript.pdf', 'manuscript.aux']:
    shutil.copy2(root / name, backup / name)
archive_header = '% BEGIN PRESERVED RANK-PROBABILITY EXPOSITION (2026-11-25)\n'
archive = ''.join('%' + line + '\n' for line in previous_fragment.splitlines())
updated = (updated_active + r'\end{document}' + archives).rstrip('\n') + '\n\n'
updated += archive_header + archive + '% END PRESERVED RANK-PROBABILITY EXPOSITION\n'
assert path.read_bytes() == original_bytes
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))

def numbered(text):
    equations = {}
    for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', text, re.S):
        body = match.group(2)
        canonical = re.sub(r'\s+', '', re.sub(r'\\label\{[^}]+\}', '', body))
        for label in re.findall(r'\\label\{([^}]+)\}', body):
            equations[label] = canonical
    return equations

code = '\n'.join(line.split('%', 1)[0] for line in updated_active.splitlines())
labels = re.findall(r'\\label\{([^}]+)\}', code)
refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', code)
report = {
    'backup': str(backup),
    'numbered_equations_unchanged': numbered(active) == numbered(updated_active),
    'numbered_equation_count': len(numbered(updated_active)),
    'prefix_before_local_edit_unchanged': updated_active[:start] == active[:start],
    'text_after_proposition_proof_unchanged': active[prop_end:] in updated_active,
    'all_previous_comment_archives_preserved': archives in updated,
    'original_fragment_preserved_in_comments': ''.join(line[1:] for line in archive.splitlines(keepends=True)).rstrip('\n') == previous_fragment.rstrip('\n'),
    'unused_cdf_band_aliases_removed_from_active_text': not re.search(r'[LU]_\\theta', updated_active),
    'duplicate_labels': [key for key, count in collections.Counter(labels).items() if count > 1],
    'undefined_references': sorted(set(refs) - set(labels)),
    'manual_sized_delimiters': re.findall(r'\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])', code),
}
Path('tmp/rank_probability_exposition_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
assert all(report[key] for key in ['numbered_equations_unchanged', 'prefix_before_local_edit_unchanged',
    'text_after_proposition_proof_unchanged', 'all_previous_comment_archives_preserved',
    'original_fragment_preserved_in_comments', 'unused_cdf_band_aliases_removed_from_active_text'])
assert not any(report[key] for key in ['duplicate_labels', 'undefined_references', 'manual_sized_delimiters'])
