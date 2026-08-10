#!/usr/bin/env python3
"""Validate targets.json against schema.json."""
import json, sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("Install jsonschema: pip install jsonschema")
    sys.exit(1)

BASE = Path(__file__).parent
targets = json.loads((BASE / "targets.json").read_text())
schema  = json.loads((BASE / "schema.json").read_text())

all_pass = True
print(f"Validating {len(targets)} targets...\n")
for t in targets:
    errors = list(jsonschema.Draft7Validator(schema["items"]).iter_errors(t))
    seq_ok = len(t.get("protein_sequence","")) >= 100
    if errors or not seq_ok:
        all_pass = False
        print(f"  FAIL  {t.get('id','?')}")
        for e in errors:
            print(f"        ✘ {e.message}")
        if not seq_ok:
            print(f"        ✘ sequence too short ({len(t.get('protein_sequence',''))} aa)")
    else:
        print(f"  PASS  {t['id']:8s}  tier={t['difficulty_tier']}  "
              f"seq={len(t['protein_sequence'])} aa  drugs={len(t['known_drugs'])}")

print()
if all_pass:
    print("All targets PASS ✔")
    sys.exit(0)
else:
    print("Some targets FAILED ✘")
    sys.exit(1)
