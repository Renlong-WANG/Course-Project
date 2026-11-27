from datetime import datetime
from pathlib import Path
import hashlib
import json
import shutil

root = Path.cwd()
path = root / 'manuscript.tex'
previous_bytes = path.read_bytes()
previous = previous_bytes.decode('utf-8').replace('\r\n', '\n')
start = previous.index(r'\section{Tractable Reformulation}')
tail_start = previous.index('The same formulas give the response-threshold curves', start)
section_end = previous.index('% BEGIN OPTIONAL APPENDIX:', tail_start)
previous_section = previous[start:section_end]
core = (root / 'tmp/partition_duality_section4_core.tex').read_text(encoding='utf-8').rstrip() + '\n\n'
assert core.startswith(r'\section{Tractable Reformulation}')
assert core.count(r'\begin{proof}') == core.count(r'\end{proof}') == 4
assert core.count(r'\begin{lemma}') == core.count(r'\end{lemma}') == 1
backup = root / 'backups' / ('partition_duality_20261125_' + datetime.now().strftime('%H%M%S'))
backup.mkdir(parents=True)
for name in ['manuscript.tex', 'manuscript.pdf', 'reference.bib', 'manuscript.aux']:
    if (root / name).exists():
        shutil.copy2(root / name, backup / name)
updated = previous[:start] + core + previous[tail_start:]
header = '% BEGIN PRESERVED SECTION 4 BEFORE PARTITION-BASED DUALITY REWRITE (2026-11-25)\n'
assert header not in previous
archive = ''.join('%' + line for line in previous_section.splitlines(keepends=True))
updated = updated.rstrip('\n') + '\n\n' + header + archive + '% END PRESERVED SECTION 4 BEFORE PARTITION-BASED DUALITY REWRITE\n'
assert path.read_bytes() == previous_bytes, 'Source changed while preparing the rewrite.'
path.write_bytes(updated.replace('\n', '\r\n').encode('utf-8'))
report = {
    'backup': str(backup),
    'source_sha256_before': hashlib.sha256(previous_bytes).hexdigest(),
    'sections_1_to_3_unchanged': updated[:start] == previous[:start],
    'existing_threshold_curves_and_discussion_preserved': previous[tail_start:] in updated,
    'original_section_commented_exactly': ''.join(line[1:] for line in archive.splitlines(keepends=True)) == previous_section,
    'new_core_lines': len(core.splitlines()),
}
(root / 'tmp/partition_duality_rewrite_state.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
assert all(report[key] for key in ['sections_1_to_3_unchanged', 'existing_threshold_curves_and_discussion_preserved', 'original_section_commented_exactly'])
print(json.dumps(report, indent=2))
