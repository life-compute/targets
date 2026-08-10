# LIFE Compute — Cancer Target Database

A curated, structured database of **10 validated cancer drug targets** built for the LIFE Compute drug discovery platform. Each entry includes the canonical protein sequence, structural reference data, difficulty classification, known clinical drugs, and scoring parameters for computational drug screening.

---

## Target Summary

| ID | UniProt | Protein Name | Disease Focus | Difficulty | Known Drugs |
|----------|---------|----------------------------------------------|-------------------------------|------------|-------------|
| TP53 | P04637 | Cellular tumor antigen p53 | Pan-cancer (>50% of tumors) | ⭐⭐⭐ Tier 3 | 3 |
| BRCA1 | P38398 | Breast cancer type 1 susceptibility protein | Breast & Ovarian Cancer | ⭐⭐⭐ Tier 3 | 4 |
| EGFR | P00533 | Epidermal growth factor receptor | NSCLC, Head & Neck, CRC | ⭐⭐ Tier 2 | 4 |
| ERBB2 | P04626 | Receptor tyrosine-protein kinase erbB-2 (HER2) | Breast, Gastric Cancer | ⭐⭐ Tier 2 | 4 |
| KRAS | P01116 | GTPase KRas | Pancreatic, Lung, Colorectal | ⭐⭐⭐ Tier 3 | 3 |
| BCL2 | P10415 | Apoptosis regulator Bcl-2 | CLL, Lymphoma | ⭐⭐ Tier 2 | 2 |
| CDK4 | P11802 | Cyclin-dependent kinase 4 | Breast Cancer, Liposarcoma | ⭐ Tier 1 | 3 |
| KDR | P35968 | VEGFR2 (KDR/FLK1) | RCC, HCC, NSCLC (angiogenesis)| ⭐⭐ Tier 2 | 4 |
| CD274 | Q9NZQ7 | PD-L1 (CD274/B7-H1) | Pan-cancer immune checkpoint | ⭐ Tier 1 | 3 |
| MDM2 | Q00987 | E3 ubiquitin-protein ligase Mdm2 (HDM2) | Sarcoma, AML, p53 wt tumors | ⭐ Tier 1 | 3 |

**Difficulty tiers:** Tier 1 = well-characterized druggable pocket, Tier 2 = moderate challenges, Tier 3 = historically challenging or "undruggable"

---

## Repository Structure

```
targets/
├── targets.json      # The 10-target database (canonical sequences, drugs, scoring params)
├── schema.json       # JSON Schema (draft-07) for targets.json
├── validate.py       # Validation script — run to verify database integrity
├── README.md         # This file
└── CONTRIBUTING.md   # How to propose new targets
```

---

## Quick Start

### Validate the database
```bash
pip install jsonschema
python3 validate.py
```

### Load targets in Python
```python
import json

with open("targets.json") as f:
    targets = json.load(f)

# Access a specific target
egfr = next(t for t in targets if t["id"] == "EGFR")
print(f"EGFR sequence length: {len(egfr['protein_sequence'])} aa")
print(f"Reference structure:  {egfr['pdb_id']}")
print(f"Score threshold:      {egfr['target_score_threshold']} kcal/mol")
print(f"Active site residues: {egfr['active_site_residues']}")
```

---

## Schema Documentation

Each target in `targets.json` is a JSON object with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Short gene/protein identifier (primary key, e.g. `"EGFR"`) |
| `uniprot_id` | string | UniProt accession for the canonical human sequence (e.g. `"P00533"`) |
| `protein_name` | string | Full recommended protein name per UniProt |
| `protein_sequence` | string | Complete canonical amino acid sequence (single-letter IUPAC, no gaps) |
| `disease_context` | string | 1-3 sentence description of the protein's role in cancer |
| `difficulty_tier` | integer (1–3) | Drug discovery difficulty: 1=easiest, 3=hardest |
| `difficulty_rationale` | string | Scientific justification for the assigned tier |
| `known_drugs` | array | 2–6 clinically relevant drugs (see sub-fields below) |
| `scoring_metric` | string | `"binding_affinity_kcal_mol"` or `"docking_score"` |
| `target_score_threshold` | float | Minimum score to classify a molecule as a hit |
| `pdb_id` | string | RCSB PDB accession for the reference crystal structure |
| `active_site_residues` | array of int | Key residue positions (1-indexed, UniProt numbering) for docking |

### `known_drugs` sub-fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Drug name (generic + code name) |
| `mechanism` | string | Pharmacological mechanism of action |
| `approved_year` | integer or null | First regulatory approval year; null if investigational |

Full schema with constraints, patterns, and descriptions is in [`schema.json`](./schema.json).

---

## How to Add New Targets

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full process. In brief:

1. **Check eligibility:** The target must be a validated cancer drug target with at least one crystal structure in the PDB and at least 2 known drugs or clinical-stage compounds.

2. **Prepare the entry:** Follow the schema exactly. Fetch the canonical sequence from UniProt (`https://rest.uniprot.org/uniprotkb/<UNIPROT_ID>.fasta`).

3. **Validate:** Run `python3 validate.py` and confirm your new entry produces `PASS`.

4. **Open a PR:** Submit a pull request with the updated `targets.json`, a brief scientific rationale in the PR description, and at least one supporting reference.

5. **Review:** The LIFE Compute scientific committee reviews for accuracy, completeness, and clinical relevance.

---

## Data Sources & Accuracy

All data in this database is derived from peer-reviewed literature and authoritative databases:

- **Protein sequences:** [UniProt/Swiss-Prot](https://www.uniprot.org/) canonical human sequences
- **Structural data:** [RCSB Protein Data Bank](https://www.rcsb.org/)
- **Drug approvals:** [FDA Orange Book](https://www.accessdata.fda.gov/scripts/cder/ob/), [Drugs@FDA](https://www.accessdata.fda.gov/scripts/cder/daf/), [EMA EPAR](https://www.ema.europa.eu/en/medicines/epar-product-index)
- **Disease context:** [COSMIC](https://cancer.sanger.ac.uk/cosmic), [cBioPortal](https://www.cbioportal.org/), primary literature

---

## License

MIT License — see [LICENSE](./LICENSE) file.

Copyright © 2025 LIFE Compute Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
