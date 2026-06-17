#!/usr/bin/env python3
"""Bundle a fixture run's outputs for publishing as the contract-fixtures Release.

For each output the plan declares, copy the file the run produced into:

    <dest>/by-id/<output-id>   one known-good example per stage output
    <dest>/manifest.json       output-id -> sha256, plus provenance

Run after `ob run ... --out-dir out_ci`. See docs/contract-fixtures.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# omnibenchmark bookkeeping dirs; the ".<hash>" param dirs holding outputs are kept.
META = {".snakemake", ".modules", ".metadata", ".envs", ".logs", ".git"}


def sh(*cmd: str) -> str:
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find(out_dir: Path, filename: str) -> Path | None:
    """First file named `filename` in the run tree (any valid producer will do)."""
    hits = [p for p in sorted(out_dir.rglob(filename)) if not set(p.parts) & META]
    return hits[0] if hits else None


def provenance(out_dir: Path, dataset: str) -> dict:
    """Where these came from: this dataset, this plan commit, this CI run."""
    repo, run = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_RUN_ID")
    meta = out_dir / ".metadata" / "manifest.json"
    ob = json.loads(meta.read_text()) if meta.exists() else {}
    return {
        "note": "structural fixtures from one tiny dataset on one CI run; not a reproducible result",
        "dataset": dataset,
        "plan_commit": os.environ.get("GITHUB_SHA") or sh("git", "rev-parse", "HEAD"),
        "run_url": f"https://github.com/{repo}/actions/runs/{run}" if repo and run else None,
        "ob_version": ob.get("ob_version"),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", type=Path, default=Path("out_ci"))
    ap.add_argument("--plan", type=Path, default=Path("benchmark_conda.yaml"))
    ap.add_argument("--dataset", default="be1")
    ap.add_argument("--dest", type=Path, default=Path("contract-bundle"))
    a = ap.parse_args()

    shutil.rmtree(a.dest, ignore_errors=True)
    (a.dest / "by-id").mkdir(parents=True)

    declared = json.loads(sh("yq", "-o=json", "[.stages[].outputs[]]", str(a.plan)))
    outputs, missing = {}, []
    for o in declared:
        src = find(a.out_dir, o["path"].replace("{dataset}", a.dataset))
        if not src:
            missing.append(o["id"])
            continue
        shutil.copy2(src, a.dest / "by-id" / o["id"])
        outputs[o["id"]] = {"sha256": sha256(src), "producer": str(src.relative_to(a.out_dir))}

    manifest = {
        "provenance": provenance(a.out_dir, a.dataset),
        "api_version": sh("yq", "-r", ".api_version", str(a.plan)),
        "outputs": outputs,
    }
    (a.dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"bundled {len(outputs)} outputs -> {a.dest}/")
    if missing:
        print(f"skipped (not produced by this run): {', '.join(missing)}")


if __name__ == "__main__":
    main()
