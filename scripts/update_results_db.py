#!/usr/bin/env python3
"""
LIFE Compute — Results Database Updater
scripts/update_results_db.py

Called by the miner daemon after each confirmed $LIFE mint.
Updates data/results/ in a local clone of life-compute/targets and pushes to GitHub.

Usage (from miner):
    python scripts/update_results_db.py \\
        --smiles "CC(=O)Oc1ccccc1C(=O)O" \\
        --score -8.42 \\
        --target EGFR \\
        --uniprot P00533 \\
        --wallet 4zn1WQZy48ysUeSo2WCFwF9LmoPhZedZq7iKLcAH3pc8 \\
        --epoch 17 \\
        --tx 5JW... \\
        --life-earned 5000000

Environment variables:
    TARGETS_REPO_DIR   Local clone of life-compute/targets (default: /tmp/life-compute/targets)
    GITHUB_TOKEN       Token for push (optional — uses configured git credentials if absent)
    SKIP_GIT_PUSH      Set to "1" to update files without pushing (for testing)
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("results-db")

TARGETS_REPO = Path(os.environ.get("TARGETS_REPO_DIR", "/tmp/life-compute/targets"))
RESULTS_DIR  = TARGETS_REPO / "data" / "results"
HITS_JSON       = RESULTS_DIR / "hits.json"
DAILY_JSON      = RESULTS_DIR / "daily_report.json"
LEADERBOARD_JSON = RESULTS_DIR / "leaderboard.json"
STATS_JSON      = RESULTS_DIR / "network_stats.json"

TOP_N = 10   # molecules per target in leaderboard


# ── JSON helpers ──────────────────────────────────────────────────────────────

def load(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


# ── Core update logic ─────────────────────────────────────────────────────────

def add_hit(smiles: str, score: float, target_id: str, uniprot_id: str,
            miner_wallet: str, epoch: int, tx: str, life_earned: int) -> dict:
    """Build a single hit record."""
    return {
        "smiles":       smiles,
        "boltz_score":  score,
        "target_id":    target_id,
        "uniprot_id":   uniprot_id,
        "miner_wallet": miner_wallet,
        "epoch":        epoch,
        "tx":           tx,
        "life_earned":  life_earned,
        "timestamp":    datetime.now(timezone.utc).isoformat(),
    }


def update_hits(hit: dict) -> None:
    """Append hit to hits.json."""
    data = load(HITS_JSON)
    hits = data.get("hits", [])
    # Deduplicate by tx — idempotent if called twice for the same mint
    if any(h.get("tx") == hit["tx"] for h in hits):
        log.info(f"Hit already in hits.json (tx={hit['tx'][:16]}…) — skipping")
        return
    hits.append(hit)
    data["hits"] = hits
    save(HITS_JSON, data)
    log.info(f"hits.json: {len(hits)} total hits")


def rebuild_leaderboard() -> None:
    """Rebuild leaderboard.json — top N per target by boltz_score (most negative wins)."""
    hits = load(HITS_JSON).get("hits", [])
    by_target = defaultdict(list)
    for h in hits:
        by_target[h["target_id"]].append(h)

    targets_out = {}
    for tid, target_hits in by_target.items():
        # Sort: lower (more negative) score = better binding
        ranked = sorted(target_hits, key=lambda h: h["boltz_score"])[:TOP_N]
        targets_out[tid] = [
            {
                "rank":         i + 1,
                "smiles":       h["smiles"],
                "boltz_score":  h["boltz_score"],
                "miner_wallet": h["miner_wallet"],
                "uniprot_id":   h.get("uniprot_id", ""),
                "epoch":        h["epoch"],
                "tx":           h["tx"],
                "timestamp":    h["timestamp"],
            }
            for i, h in enumerate(ranked)
        ]

    data = load(LEADERBOARD_JSON)
    data["targets"] = targets_out
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    save(LEADERBOARD_JSON, data)
    log.info(f"leaderboard.json: {len(targets_out)} targets with entries")


def rebuild_daily_report() -> None:
    """Rebuild daily_report.json — best hit per target for today (UTC)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    hits = load(HITS_JSON).get("hits", [])

    today_hits = [h for h in hits if h.get("timestamp", "").startswith(today)]
    by_target = defaultdict(list)
    for h in today_hits:
        by_target[h["target_id"]].append(h)

    entries = []
    for tid, target_hits in by_target.items():
        best = min(target_hits, key=lambda h: h["boltz_score"])
        entries.append({
            "date":         today,
            "target_id":    tid,
            "uniprot_id":   best.get("uniprot_id", ""),
            "best_smiles":  best["smiles"],
            "best_score":   best["boltz_score"],
            "miner_wallet": best["miner_wallet"],
            "tx":           best["tx"],
            "total_hits":   len(target_hits),
        })

    entries.sort(key=lambda e: e["best_score"])  # best targets first

    data = load(DAILY_JSON)
    data["report_date"] = today
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    data["entries"] = entries
    save(DAILY_JSON, data)
    log.info(f"daily_report.json: {len(entries)} targets have hits today")


def update_network_stats(hit: dict) -> None:
    """Update network_stats.json counters from this new hit."""
    data = load(STATS_JSON)
    hits = load(HITS_JSON).get("hits", [])

    # Recount from canonical hits.json
    confirmed = len(hits)
    total_life = sum(h.get("life_earned", 0) for h in hits)
    unique_targets = len({h["target_id"] for h in hits})

    data["confirmed_hits"]      = confirmed
    data["life_minted_raw"]     = total_life
    data["life_minted_display"] = f"{total_life / 1_000_000:.6f}"
    data["targets_solved"]      = unique_targets
    data["last_hit_at"]         = hit["timestamp"]
    data["last_hit_target"]     = hit["target_id"]
    data["last_hit_score"]      = hit["boltz_score"]
    data["last_updated"]        = datetime.now(timezone.utc).isoformat()

    # molecules_screened is a superset — keep if already larger
    data["molecules_screened"] = max(data.get("molecules_screened", 0), confirmed)

    save(STATS_JSON, data)
    log.info(f"network_stats.json: {confirmed} hits, {total_life/1e6:.3f} $LIFE minted, "
             f"{unique_targets} targets solved")


# ── Git push ──────────────────────────────────────────────────────────────────

def git_push(hit: dict) -> bool:
    """Commit and push results to GitHub. Returns True on success."""
    if os.environ.get("SKIP_GIT_PUSH") == "1":
        log.info("SKIP_GIT_PUSH=1 — skipping git push")
        return True

    repo = TARGETS_REPO
    files = [
        "data/results/hits.json",
        "data/results/leaderboard.json",
        "data/results/daily_report.json",
        "data/results/network_stats.json",
    ]
    try:
        subprocess.run(["git", "add"] + files, cwd=repo, check=True)
        msg = (f"results: confirmed hit {hit['target_id']} score={hit['boltz_score']:.3f} "
               f"epoch={hit['epoch']} tx={hit['tx'][:16]}…")
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo)
        if result.returncode == 0:
            log.info("No changes to commit — results unchanged")
            return True
        subprocess.run(["git", "commit", "-m", msg], cwd=repo, check=True)
        subprocess.run(["git", "push", "origin", "master"], cwd=repo, check=True)
        log.info(f"Pushed results to github.com/life-compute/targets")
        return True
    except subprocess.CalledProcessError as e:
        log.warning(f"git push failed: {e} — results saved locally, will push next run")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Update LIFE Compute results database")
    parser.add_argument("--smiles",      required=True)
    parser.add_argument("--score",       required=True, type=float,
                        help="Boltz2 ΔG in kcal/mol (negative number)")
    parser.add_argument("--target",      required=True, dest="target_id")
    parser.add_argument("--uniprot",     required=True, dest="uniprot_id")
    parser.add_argument("--wallet",      required=True, dest="miner_wallet")
    parser.add_argument("--epoch",       required=True, type=int)
    parser.add_argument("--tx",          required=True)
    parser.add_argument("--life-earned", required=True, type=int, dest="life_earned",
                        help="Raw token units (multiply display value by 1e6)")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Ensure all four files exist (first-run bootstrap)
    for path, default in [
        (HITS_JSON,        {"_schema": "life-compute/hits v1", "hits": []}),
        (DAILY_JSON,       {"_schema": "life-compute/daily_report v1", "entries": []}),
        (LEADERBOARD_JSON, {"_schema": "life-compute/leaderboard v1", "targets": {}}),
        (STATS_JSON,       {"_schema": "life-compute/network_stats v1"}),
    ]:
        if not path.exists():
            save(path, default)

    hit = add_hit(
        smiles=args.smiles, score=args.score,
        target_id=args.target_id, uniprot_id=args.uniprot_id,
        miner_wallet=args.miner_wallet, epoch=args.epoch,
        tx=args.tx, life_earned=args.life_earned,
    )

    update_hits(hit)
    rebuild_leaderboard()
    rebuild_daily_report()
    update_network_stats(hit)
    git_push(hit)

    log.info("Results database updated successfully.")


if __name__ == "__main__":
    main()
