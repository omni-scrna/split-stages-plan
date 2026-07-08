#!/usr/bin/env python
"""Build a tiny CI fixture by subsampling the real `be1` dataset.

Cells are subsampled (stratified across `Sample` so every category survives);
*all genes are kept* so no downstream module can miss a gene/var it expects.
Outputs the same three files the `DATA` stage declares, into fixtures/DATA/:
    be1.h5ad, be1.clusters_truth.tsv, be1.clusters_truth_num.txt

Run with an env that has anndata, e.g.:
    out/.snakemake/conda/<scanpy-env>/bin/python fixtures/build_fixture.py
"""

import os

import anndata as ad
import h5py
import numpy as np
import pandas as pd

SRC_H5AD = "out/DATA/datasets/.3d6ce691/datasets.h5ad"
SRC_TRUTH = "out/DATA/datasets/.3d6ce691/datasets.clusters_truth.tsv"
OUT_DIR = "fixtures/DATA"
# Cells kept per Sample. Seurat RPCA integration integrates on the precomputed
# PCA (n_components=50) and errors if any *batch layer* has fewer cells than the
# dim count -- "At least one layer has fewer cells than dimensions specified".
# So every Sample must clear 50 cells *after* filtering. Retention is highly
# uneven: cell lines keep ~70-100%, but PBMC keeps only ~28% (60 -> 17), so the
# per-Sample cap has to be sized off that worst case: 50 / 0.28 ~= 180, plus
# margin. 250 lands the smallest layer around ~70 post-filter.
N_PER_GROUP = 250
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

    out_h5ad = os.path.join(OUT_DIR, "be1.h5ad")
    sub.write_h5ad(out_h5ad)

    # anndata.write_h5ad serializes string obs/var columns as *categorical*
    # groups (categories + codes). The real `1-data` module (written in R)
    # emits flat string arrays instead, and the R downstream modules read obs
    # columns with rhdf5::h5read, which expects a flat array and mangles a
    # categorical group into a degenerate batch vector (e.g. Seurat RPCA
    # integration then splits `Sample` into 1-cell layers and fails). Rewrite
    # every categorical column as a dense string-array to match the real
    # dataset's on-disk encoding.
    _decategoricalize(out_h5ad)

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


def _decategoricalize(path):
    """Replace categorical obs/var columns with dense string-array datasets."""
    str_dt = h5py.string_dtype(encoding="utf-8")
    with h5py.File(path, "r+") as f:
        for section in ("obs", "var"):
            for col, node in list(f[section].items()):
                if node.attrs.get("encoding-type") != "categorical":
                    continue
                cats = node["categories"].asstr()[:]
                codes = node["codes"][:]
                if codes.min() < 0:
                    raise ValueError(f"{section}/{col} has NaN codes (-1); "
                                     "string-array cannot represent them")
                del f[f"{section}/{col}"]
                dset = f[section].create_dataset(col, data=cats[codes], dtype=str_dt)
                dset.attrs["encoding-type"] = "string-array"
                dset.attrs["encoding-version"] = "0.2.0"


if __name__ == "__main__":
    main()
