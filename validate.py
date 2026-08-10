#!/usr/bin/env python3
"""
validate.py — LIFE Compute Cancer Target Database Validator
============================================================
Validates targets.json against schema.json and performs additional
domain-specific quality checks.

Usage:
    python3 validate.py [--targets targets.json] [--schema schema.json]

Exit codes:
    0 — all targets passed
    1 — one or more targets failed validation
"""

import json
import sys
import argparse
from pathlib import Path

try:
    import jsonschema
    from jsonschema import validate, ValidationError, Draft7Validator
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema")
    sys.exit(1)

# Minimum plausible sequence lengths per target (aa)
MIN_SEQUENCE_LENGTH = 100

# Known UniProt IDs and their expected minimum lengths
EXPECTED_MIN_LENGTHS = {
    "P04637": 390,   # TP53
    "P38398": 1800,  # BRCA1
    "P00533": 1200,  # EGFR
    "P04626": 1250,  # HER2
    "P01116": 185,   # KRAS
    "P10415": 230,   # BCL2
    "P11802": 295,   # CDK4
    "P35968": 1350,  # VEGFR2/KDR
    "Q9NZQ7": 285,   # PD-L1/CD274
    "Q00987": 485,   # MDM2
}

VALID_AA = set("ACDEFGHIKLMNPQRSTVWY")


def check_sequence(target_id: str, uniprot_id: str, sequence: str) -> list[str]:
    """Domain-specific sequence quality checks beyond JSON Schema validation."""
    issues = []

    # Length check
    if len(sequence) < MIN_SEQUENCE_LENGTH:
        issues.append(
            f"Sequence too short: {len(sequence)} aa (minimum {MIN_SEQUENCE_LENGTH} aa)"
        )

    # Known minimum length check
    if uniprot_id in EXPECTED_MIN_LENGTHS:
        expected_min = EXPECTED_MIN_LENGTHS[uniprot_id]
        if len(sequence) < expected_min:
            issues.append(
                f"Sequence for {uniprot_id} appears truncated: "
                f"{len(sequence)} aa (expected >= {expected_min} aa for canonical sequence)"
            )

    # Valid amino acid characters
    invalid_chars = set(sequence) - VALID_AA
    if invalid_chars:
        issues.append(
            f"Sequence contains non-standard amino acid characters: {sorted(invalid_chars)}"
        )

    # No whitespace in sequence
    if any(c.isspace() for c in sequence):
        issues.append("Sequence contains whitespace — remove all spaces and newlines")

    return issues


def check_active_site_residues(target_id: str, sequence: str, residues: list) -> list[str]:
    """Check that active site residue positions are within sequence bounds."""
    issues = []
    seq_len = len(sequence)
    out_of_bounds = [r for r in residues if r > seq_len]
    if out_of_bounds:
        issues.append(
            f"Active site residues out of sequence bounds (seq len={seq_len}): {out_of_bounds}"
        )
    return issues


def check_known_drugs(target_id: str, known_drugs: list) -> list[str]:
    """Sanity-check drug entries."""
    issues = []
    if len(known_drugs) < 2:
        issues.append("Must have at least 2 known drugs")
    for drug in known_drugs:
        if len(drug.get("name", "")) < 3:
            issues.append(f"Drug name too short: '{drug.get('name')}'")
        if len(drug.get("mechanism", "")) < 20:
            issues.append(f"Drug mechanism description too short: '{drug.get('name')}'")
    return issues


def validate_target(target: dict, schema_validator: Draft7Validator) -> tuple[bool, list[str]]:
    """Run all validations on a single target. Returns (passed, list_of_issues)."""
    all_issues = []

    # 1. JSON Schema validation
    schema_errors = list(schema_validator.iter_errors(target))
    if schema_errors:
        for error in schema_errors:
            path = " -> ".join(str(p) for p in error.absolute_path) or "(root)"
            all_issues.append(f"Schema error at [{path}]: {error.message}")

    # 2. Sequence quality checks
    seq_issues = check_sequence(
        target.get("id", "?"),
        target.get("uniprot_id", ""),
        target.get("protein_sequence", ""),
    )
    all_issues.extend(seq_issues)

    # 3. Active site residue bounds check
    if "protein_sequence" in target and "active_site_residues" in target:
        as_issues = check_active_site_residues(
            target.get("id", "?"),
            target["protein_sequence"],
            target["active_site_residues"],
        )
        all_issues.extend(as_issues)

    # 4. Known drugs check
    if "known_drugs" in target:
        drug_issues = check_known_drugs(target.get("id", "?"), target["known_drugs"])
        all_issues.extend(drug_issues)

    passed = len(all_issues) == 0
    return passed, all_issues


def main():
    parser = argparse.ArgumentParser(description="Validate LIFE Compute targets.json")
    parser.add_argument(
        "--targets",
        default=Path(__file__).parent / "targets.json",
        type=Path,
        help="Path to targets.json (default: targets.json in same directory)",
    )
    parser.add_argument(
        "--schema",
        default=Path(__file__).parent / "schema.json",
        type=Path,
        help="Path to schema.json (default: schema.json in same directory)",
    )
    args = parser.parse_args()

    # Load files
    print(f"Loading targets from: {args.targets}")
    with open(args.targets) as f:
        targets = json.load(f)

    print(f"Loading schema from:  {args.schema}")
    with open(args.schema) as f:
        schema = json.load(f)

    print(f"\nValidating {len(targets)} target(s)...\n")
    print(f"{'ID':<12} {'UniProt':<10} {'Seq Len':>8} {'Drugs':>6} {'Tier':>5}  STATUS")
    print("-" * 70)

    validator = Draft7Validator(schema["items"])  # validate each item individually
    all_passed = True
    results = []

    for target in targets:
        target_id = target.get("id", "UNKNOWN")
        uniprot_id = target.get("uniprot_id", "?")
        seq_len = len(target.get("protein_sequence", ""))
        num_drugs = len(target.get("known_drugs", []))
        tier = target.get("difficulty_tier", "?")

        passed, issues = validate_target(target, validator)
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"{target_id:<12} {uniprot_id:<10} {seq_len:>8} {num_drugs:>6} {tier:>5}  {status}")
        if issues:
            for issue in issues:
                print(f"             └─ {issue}")

        results.append((target_id, passed, issues))
        if not passed:
            all_passed = False

    print("-" * 70)
    passed_count = sum(1 for _, p, _ in results if p)
    print(f"\nSummary: {passed_count}/{len(results)} targets passed validation\n")

    if all_passed:
        print("✅ ALL TARGETS PASSED — targets.json is valid and ready for use.")
        sys.exit(0)
    else:
        failed = [(id_, issues) for id_, passed, issues in results if not passed]
        print(f"❌ VALIDATION FAILED — {len(failed)} target(s) have issues:")
        for target_id, issues in failed:
            print(f"\n  {target_id}:")
            for issue in issues:
                print(f"    - {issue}")
        sys.exit(1)


if __name__ == "__main__":
    main()
