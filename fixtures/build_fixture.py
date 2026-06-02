#!/usr/bin/env python
"""Build a tiny CI fixture by subsampling the real `be1` dataset.

Cells are subsampled (stratified across `Sample` so every category survives);
*all genes are kept* so no downstream module can miss a gene/var it expects.
Outputs the same three files the `one-data` stage declares, into fixtures/1-data/:
    be1.h5ad, be1.clusters_truth.tsv, be1.clusters_truth_num.txt

Run with an env that has anndata, e.g.:
    out/.snakemake/conda/<scanpy-env>/bin/python fixtures/build_fixture.py
"""

import os

import anndata as ad
import numpy as np
import pandas as pd

SRC_H5AD = "out/one-data/datasets/.3d6ce691/datasets.h5ad"
SRC_TRUTH = "out/one-data/datasets/.3d6ce691/datasets.clusters_truth.tsv"
OUT_DIR = "fixtures/1-data"
N_PER_GROUP = 40       # cells kept per Sample; >50 total ensures PCA(n=50) works
STRATIFY = "Sample"
SEED = 0


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rng = np.random.default_rng(SEED)

    a = ad.read_h5ad(SRC_H5AD)
    print(f"source: {a.shape[0]} cells x {a.shape[1]} genes; X={'present' if a.X is not None else 'None'}")

    # Stratified cell subsample: up to N_PER_GROUP per Sample, keep every category.
    keep = []
    for grp, idx in a.obs.groupby(STRATIFY, observed=True).indices.items():
        n = min(N_PER_GROUP, len(idx))
        keep.extend(rng.choice(idx, size=n, replace=False).tolist())
    keep = sorted(keep)
    sub = a[keep].copy()          # all genes kept
    print(f"fixture: {sub.shape[0]} cells x {sub.shape[1]} genes")
    print("Sample counts:", sub.obs[STRATIFY].value_counts().to_dict())

    sub.write_h5ad(os.path.join(OUT_DIR, "be1.h5ad"))

    # Subset the truth TSV to the same cells (join on cell_id == obs_names).
    truth = pd.read_csv(SRC_TRUTH, sep="\t")
    id_col = truth.columns[0]
    truth = truth[truth[id_col].isin(set(sub.obs_names))].reset_index(drop=True)
    assert len(truth) == sub.n_obs, f"truth join mismatch: {len(truth)} vs {sub.n_obs}"
    truth.to_csv(os.path.join(OUT_DIR, "be1.clusters_truth.tsv"), sep="\t", index=False)

    n_clusters = truth[truth.columns[-1]].nunique()
    with open(os.path.join(OUT_DIR, "be1.clusters_truth_num.txt"), "w") as fh:
        fh.write(f"{n_clusters}\n")
    print(f"clusters in fixture: {n_clusters}")


if __name__ == "__main__":
    main()
