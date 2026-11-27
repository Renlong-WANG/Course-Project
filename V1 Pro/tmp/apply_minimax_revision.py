from pathlib import Path
import hashlib
import json
import re

root = Path.cwd()
source = root / "manuscript.tex"
backup = root / "backups/minimax_reformulation_20261124_193920/manuscript.tex"
original_bytes = backup.read_bytes()
assert source.read_bytes() == original_bytes, "Manuscript changed since the backup; inspect before editing."
original = original_bytes.decode("utf-8")
section_start = original.index(r"\section{Tractable Reformulation}")
section_end = original.index(r"\bibliographystyle", section_start)
old_section = original[section_start:section_end]
prefix = old_section[:old_section.index("The functional multiplier has now been eliminated")]
intro_start = prefix.index("The DW ambiguity set imposes")
intro_end = prefix.index("For each empirical probability level", intro_start)
new_intro = (
    "Scalar inversion converts the DW constraint into finitely many linear restrictions on residual probabilities. "
    "We derive the Lagrangian duals, prove strong duality through compactness of the attainable probability set and a minimax exchange, "
    "and then obtain closed forms and optimal dual certificates. "
    "Throughout this section, the training data, the test residuals, and $\\theta\\ge0$ are fixed; "
    "$\\mathcal X$ is a Borel subset of $\\mathbb R^n$, and $\\hat g$ is Borel measurable. "
    "The main results use the default residual support $\\mathcal E=\\mathbb R$; known interval support is treated at the end.\n\n"
)
prefix = prefix[:intro_start] + new_intro + prefix[intro_end:]
interpretation_start = prefix.index("To interpret the resulting probability bounds")
measure_start = prefix.index("Substituting \\eqref{eq-finite-rank-constraints}", interpretation_start)
prefix = prefix[:interpretation_start] + prefix[measure_start:]
new_after_lemma = (root / "tmp/minimax_section_after_lemma.tex").read_text(encoding="utf-8")
new_section = prefix.replace("\r\n", "\n").rstrip() + "\n\n" + new_after_lemma.rstrip() + "\n\n\n"
new_section = new_section.replace("thm-finite-dual-reformulations", "thm-strong-duality")
new_section = new_section.replace("\n", "\r\n")
archive_begin = "% BEGIN PRESERVED SECTION 4 BEFORE MINIMAX REVISION (2026-11-24)\r\n"
archive_end = "% END PRESERVED SECTION 4 BEFORE MINIMAX REVISION\r\n"
archive = "".join("%" + line for line in old_section.splitlines(keepends=True))
assert archive.endswith("\n")
updated = original[:section_start] + new_section + original[section_end:]
updated = updated.rstrip("\r\n") + "\r\n\r\n" + archive_begin + archive + archive_end
source.write_bytes(updated.encode("utf-8"))
recovered = "".join(line[1:] for line in archive.splitlines(keepends=True))
assert recovered.encode("utf-8") == old_section.encode("utf-8")

bib = root / "reference.bib"
backup_bib = root / "backups/minimax_reformulation_20261124_193920/reference.bib"
assert bib.read_bytes() == backup_bib.read_bytes(), "Bibliography changed since backup."
new_entries = r'''
@article{S58,
  title = {On General Minimax Theorems},
  author = {Sion, Maurice},
  year = {1958},
  journal = {Pacific Journal of Mathematics},
  volume = {8},
  number = {1},
  pages = {171--176},
  doi = {10.2140/pjm.1958.8.171}
}

@article{M82,
  title = {Estimates for the Distribution Function of a Sum of Two Random Variables When the Marginal Distributions Are Fixed},
  author = {Makarov, G. D.},
  year = {1982},
  journal = {Theory of Probability \& Its Applications},
  volume = {26},
  number = {4},
  pages = {803--806},
  doi = {10.1137/1126086}
}

@misc{Z.R25,
  title = {Bounds on the Distribution of a Sum of Two Random Variables: Revisiting a Problem of {Kolmogorov} with Application to Individual Treatment Effects},
  author = {Zhang, Zhehao and Richardson, Thomas S.},
  year = {2025},
  howpublished = {arXiv:2405.08806v2},
  doi = {10.48550/arXiv.2405.08806},
  url = {https://arxiv.org/abs/2405.08806v2}
}
'''
bib_bytes = bib.read_bytes()
bib.write_bytes(bib_bytes.rstrip(b"\r\n") + b"\r\n\r\n" + new_entries.strip().replace("\n", "\r\n").encode("utf-8") + b"\r\n")

active = updated.split(r"\end{document}")[0]
active = "\n".join(line.split("%", 1)[0] for line in active.splitlines())
labels = re.findall(r"\\label\{([^}]+)\}", active)
references = re.findall(r"\\(?:eqref|ref)\{([^}]+)\}", active)
citations = set()
for group in re.findall(r"\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}", active):
    citations.update(key.strip() for key in group.split(","))
bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib.read_text(encoding="utf-8")))
report = {
    "old_section_archive_exact": recovered == old_section,
    "old_section_sha256": hashlib.sha256(old_section.encode("utf-8")).hexdigest(),
    "content_before_section_4_unchanged": updated[:section_start] == original[:section_start],
    "preexisting_source_tail_preserved": original[section_end:] in updated,
    "duplicate_labels": sorted({key for key in labels if labels.count(key) > 1}),
    "undefined_references": sorted(set(references) - set(labels)),
    "undefined_citations": sorted(citations - bib_keys),
    "active_manual_delimiters": re.findall(r"\\(?:big|Big|bigg|Bigg)[lrm]?(?![A-Za-z])", active),
    "active_dPi_occurrences": len(re.findall(r"\\mathrm\s*d\s*\\Pi", active)),
    "active_old_partition_objects": sorted(set(re.findall(r"\\mathcal [AI]_[ij]|\\pi_\{ij\}|eq-finite-(?:upper|lower)-dual|eq-cell-mass-polytope", active))),
    "active_appendix": bool(re.search(r"\\appendix\b", active)),
}
(root / "tmp/minimax_source_checks.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
assert not any(report[key] for key in ["duplicate_labels", "undefined_references", "undefined_citations", "active_manual_delimiters", "active_dPi_occurrences", "active_old_partition_objects", "active_appendix"])
