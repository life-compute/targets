# Contributing New Cancer Targets

Thank you for helping expand the LIFE Compute target database.

## Scientific Requirements

To propose a new target, it must meet **all** of the following:

1. **Cancer relevance** — documented role in tumour biology (driver mutation, amplification, or tumour microenvironment)
2. **UniProt entry** — reviewed (Swiss-Prot) canonical sequence
3. **PDB structure** — at least one experimental structure (X-ray/cryo-EM/NMR) in RCSB PDB
4. **Drug precedent** — at least one approved drug, clinical candidate, or high-quality chemical probe
5. **Active site** — at least 4 residues known to be involved in ligand binding

## Submission Template

Create a file `proposals/<YOUR_TARGET_ID>.json`:

```json
{
  "id": "TARGET",
  "uniprot_id": "PXXXXX",
  "protein_name": "Full protein name",
  "protein_sequence": "MKKL...",
  "disease_context": "One to two sentences on cancer role and mutation frequency.",
  "difficulty_tier": 2,
  "difficulty_rationale": "Why this tier based on structural and SAR considerations.",
  "known_drugs": [
    {
      "name": "Drug name",
      "mechanism": "Mechanism of action",
      "approved_year": 2020
    }
  ],
  "scoring_metric": "binding_affinity_kcal_mol",
  "target_score_threshold": -8.0,
  "pdb_id": "XXXX",
  "active_site_residues": [100, 105, 120]
}
```

## Review Process

1. Open a Pull Request with your `proposals/<TARGET>.json` file
2. The PR must pass `python3 validate.py` (CI enforced)
3. Two maintainers review for scientific accuracy
4. Approved targets are merged into `targets.json`

## What We Do Not Accept

- Targets with no PDB structure
- Targets with purely in-silico predicted sequences
- Duplicate targets (check existing `targets.json` first)
- Targets outside oncology (off-scope for v1)
