#!/usr/bin/env python3
"""Validate targets.json against schema.json.

Supports two target types:
  protein  — canonical UniProt protein targets (original schema)
  mRNA     — mRNA structure targets for small-molecule silencing (new)
"""
import json, sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("Install jsonschema: pip install jsonschema")
    sys.exit(1)

BASE    = Path(__file__).parent
targets = json.loads((BASE / "targets.json").read_text())
schema  = json.loads((BASE / "schema.json").read_text())

all_pass = True
protein_count = mrna_count = 0
print(f"Validating {len(targets)} targets...\n")

for t in targets:
    ttype = t.get("target_type", "protein")
    errors = list(jsonschema.Draft7Validator(schema["items"]).iter_errors(t))

    if ttype == "mRNA":
        # mRNA-specific checks
        rna_seq = t.get("rna_sequence", "")
        seq_ok = len(rna_seq) >= 50
        extra = []
        if not seq_ok:
            extra.append(f"rna_sequence too short ({len(rna_seq)} nt, need ≥50)")
        if t.get("difficulty_tier") != 3:
            extra.append("mRNA targets must be tier 3 (HARD)")
        if not t["id"].endswith("_mRNA"):
            extra.append("mRNA target id must end with _mRNA")

        if errors or extra:
            all_pass = False
            print(f"  FAIL  {t.get('id','?')}  [mRNA]")
            for e in errors:
                print(f"        ✘ {e.message}")
            for e in extra:
                print(f"        ✘ {e}")
        else:
            mrna_count += 1
            print(f"  PASS  {t['id']:20s}  [mRNA]  tier=3  region={t.get('mrna_region','')[:35]}")
    else:
        # Protein-specific checks
        seq_ok = len(t.get("protein_sequence", "")) >= 100
        extra = []
        if not seq_ok:
            extra.append(f"sequence too short ({len(t.get('protein_sequence',''))} aa)")

        if errors or extra:
            all_pass = False
            print(f"  FAIL  {t.get('id','?')}  [protein]")
            for e in errors:
                print(f"        ✘ {e.message}")
            for e in extra:
                print(f"        ✘ {e}")
        else:
            protein_count += 1
            print(f"  PASS  {t['id']:8s}  [protein]  tier={t['difficulty_tier']}  "
                  f"seq={len(t['protein_sequence'])} aa  drugs={len(t['known_drugs'])}")

print()
print(f"Summary: {protein_count} protein targets  |  {mrna_count} mRNA targets  |  "
      f"{len(targets)-protein_count-mrna_count} failed")
if all_pass:
    print("All targets PASS ✔")
    sys.exit(0)
else:
    print("Some targets FAILED ✘")
    sys.exit(1)
