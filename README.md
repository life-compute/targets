# LIFE Compute — Cancer Target Database

A curated, machine-readable database of validated cancer drug targets for the
[LIFE Compute](https://github.com/life-compute) decentralised drug discovery network.

Miners use this database to select protein targets, run Boltz2 structure prediction,
and submit binding affinity results on-chain.

## Targets

| ID | UniProt | Disease | Difficulty | PDB | Known Drugs |
|---|---|---|---|---|---|
| TP53 | P04637 | Pan-cancer (50% mutation rate) | ★★★ Hard | 2OCJ | 3 |
| BRCA1 | P38398 | Breast & ovarian cancer | ★★★ Hard | 1T15 | 3 |
| EGFR | P00533 | NSCLC, colorectal, head/neck | ★★ Moderate | 1IVO | 4 |
| HER2 | P04626 | Breast cancer (~20% amplified) | ★★ Moderate | 3PP0 | 4 |
| KRAS | P01116 | Pancreatic (90%), lung (30%), CRC | ★★★ Hard | 6OIM | 3 |
| BCL2 | P10415 | Follicular lymphoma, CLL | ★★ Moderate | 6O0K | 3 |
| CDK4 | P11802 | Liposarcoma, breast, lung | ★ Tractable | 2W96 | 3 |
| VEGFR2 | P35968 | Solid tumour angiogenesis | ★★ Moderate | 3VHE | 4 |
| PDL1 | Q9NZQ7 | Melanoma, NSCLC, bladder | ★ Tractable | 5C3T | 3 |
| MDM2 | Q00987 | Liposarcoma, osteosarcoma | ★ Tractable | 1T4E | 3 |

## Difficulty Tiers

| Tier | Label | Meaning |
|---|---|---|
| 1 | Tractable | Well-defined binding pocket, multiple approved drugs, clear SAR |
| 2 | Moderate | Validated target, resistance or selectivity challenges |
| 3 | Hard | Historically difficult, flat surfaces, no deep pocket, or undruggable |

## Schema

Each target in `targets.json` has:

| Field | Type | Description |
|---|---|---|
| `id` | string | Gene symbol |
| `uniprot_id` | string | UniProt accession |
| `protein_name` | string | Full IUPAC name |
| `protein_sequence` | string | Canonical amino acid sequence |
| `disease_context` | string | Role in cancer biology |
| `difficulty_tier` | int 1–3 | Druggability difficulty |
| `difficulty_rationale` | string | Structural reasoning |
| `known_drugs` | array | Name + mechanism + approved year |
| `scoring_metric` | string | `binding_affinity_kcal_mol` or `docking_score` |
| `target_score_threshold` | float | Hit threshold (kcal/mol) |
| `pdb_id` | string | RCSB PDB structure for docking |
| `active_site_residues` | int[] | Key residue positions |

Validate with:
```bash
python3 validate.py
```

## How to Add New Targets

See [CONTRIBUTING.md](CONTRIBUTING.md).

Requirements:
- UniProt canonical sequence
- At least one known drug or clinical candidate
- PDB structure suitable for docking
- Disease context with citation

## License

MIT
