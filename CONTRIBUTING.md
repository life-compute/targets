# Contributing to LIFE Compute — Cancer Target Database

Thank you for your interest in expanding the LIFE Compute cancer target database! This document explains how to propose new targets, the review criteria, and the quality standards we require for inclusion.

---

## Who Can Contribute

Anyone with relevant scientific expertise is welcome to propose new targets:
- Oncologists, cancer biologists, and medicinal chemists
- Computational chemists and structural biologists
- Academic researchers, pharmaceutical scientists, and bioinformaticians

---

## Eligibility Criteria

A cancer drug target must meet **all** of the following criteria to be considered for inclusion:

### Required
1. **Human protein:** Must be a human (Homo sapiens) protein with a canonical UniProt/Swiss-Prot entry.
2. **Cancer relevance:** Must have a clearly documented, mechanistically understood role in cancer initiation, progression, maintenance, or immune evasion — supported by at least one peer-reviewed publication in a major journal.
3. **Clinical validation:** At least **2** approved drugs OR **2** drugs in Phase 2 or later clinical trials that directly target this protein.
4. **Structural data:** At least one crystal or cryo-EM structure in the RCSB PDB at resolution ≤ 3.5 Å, suitable for computational docking.
5. **Sequence completeness:** The full canonical UniProt sequence must be available and ≥ 100 amino acids in length.

### Recommended
- Targets with known active site or allosteric pocket residues supported by structural or biochemical data
- Targets with published docking benchmarks or co-crystal structures with known ligands
- Targets addressing unmet clinical need (resistant cancers, rare histologies, pediatric oncology)

---

## Target Proposal Template

Open a GitHub Issue titled **"Target Proposal: [GENE_ID] ([UniProt accession])"** and fill in the following template:

```markdown
## Target Proposal: [GENE_ID] ([UniProt accession])

### Basic Information
- **Gene symbol:** 
- **UniProt accession:** 
- **Full protein name:** 
- **Human PDB structure(s):** (accession codes, resolution, bound ligand if any)

### Cancer Relevance
(2-4 sentences: which cancers, mutation/expression frequency, mechanism of oncogenic action)

### Drug Landscape
| Drug Name | Mechanism | Stage | Approval Year |
|-----------|-----------|-------|---------------|
|           |           |       |               |
|           |           |       |               |

### Proposed Difficulty Tier
- [ ] Tier 1 — Well-characterized, straightforward
- [ ] Tier 2 — Moderate challenges
- [ ] Tier 3 — Difficult / historically undruggable

**Rationale for tier:**

### Proposed Active Site Residues
(List residue positions in UniProt canonical sequence numbering with brief justification)

### Scoring Parameters
- Suggested scoring metric: [ ] binding_affinity_kcal_mol  [ ] docking_score
- Suggested score threshold: 
- Justification for threshold:

### Supporting References
1. 
2. 
3. (optional additional references)

### Conflicts of Interest
(Declare any financial relationships with companies developing drugs for this target)
```

---

## Submitting a Pull Request

Once your proposal has been discussed in a GitHub Issue and received positive feedback from a maintainer:

1. **Fork** the repository and create a feature branch:
   ```bash
   git checkout -b add-target-[GENE_ID]
   ```

2. **Add your entry** to `targets.json`. Follow the exact schema — all required fields must be present and valid. Fetch the canonical sequence from UniProt:
   ```python
   import urllib.request, json
   
   uid = "YOUR_UNIPROT_ID"
   url = f"https://rest.uniprot.org/uniprotkb/{uid}.fasta"
   with urllib.request.urlopen(url) as r:
       fasta = r.read().decode()
   sequence = "".join(fasta.strip().split("\n")[1:])
   print(f"Length: {len(sequence)} aa")
   ```

3. **Validate your addition:**
   ```bash
   pip install jsonschema
   python3 validate.py
   ```
   All targets including your new entry must show `PASS`.

4. **Update README.md** — add a row to the Target Summary table.

5. **Commit and push:**
   ```bash
   git add targets.json README.md
   git commit -m "Add target: [GENE_ID] ([UniProt accession])"
   git push origin add-target-[GENE_ID]
   ```

6. **Open a Pull Request** against `main` with:
   - A link to the discussion Issue
   - A brief scientific rationale (3-5 sentences)
   - Confirmation that `validate.py` passes

---

## Review Process

1. **Automated checks:** CI runs `validate.py` automatically on every PR. PRs that fail validation will not be merged.

2. **Scientific review:** At least one LIFE Compute scientific committee member reviews the target for:
   - Accuracy of UniProt sequence and PDB structure
   - Correctness of drug information (names, mechanisms, approval years)
   - Appropriateness of difficulty tier and rationale
   - Scientific accuracy of disease context

3. **Feedback cycle:** Reviewers may request corrections, clarifications, or additional evidence. Expected turnaround: 2-4 weeks.

4. **Merge:** Once approved by ≥ 1 scientific reviewer, the PR is merged into `main`.

---

## Data Accuracy Standards

We hold contributions to a high standard of scientific accuracy:

- **Sequences:** Must match the UniProt canonical sequence exactly — fetch directly from UniProt API, do not manually transcribe.
- **Drug information:** Cross-reference against FDA Drugs@FDA, EMA EPAR, or ClinicalTrials.gov. Do not include drugs that failed Phase 2 or were withdrawn for safety reasons without noting this explicitly in the mechanism field.
- **PDB structures:** Verify the accession is valid on rcsb.org and that the structure covers the therapeutically relevant domain.
- **Active site residues:** Must be supported by structural or biochemical evidence (e.g., co-crystal structure, mutagenesis study). Cite the supporting paper in your PR description.

---

## Code of Conduct

All contributors are expected to adhere to scientific integrity standards:
- No fabricated or unverified data
- Declare conflicts of interest transparently
- Engage respectfully with reviewers and other contributors
- Do not propose targets solely to benefit a commercial interest without disclosure

---

## Questions?

Open a GitHub Issue labeled `question` or contact the LIFE Compute maintainers via the repository discussion board.
