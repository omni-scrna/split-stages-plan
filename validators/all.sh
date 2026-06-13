#!/bin/sh
# Run all validator scripts against the default out/ folder
# This is a rudimentary script that executes benchmarker code against a fixed path.
# To be run from the root folder of the plan with a the default "out" folder.
# Just concerned about quick sanity checks for now. We expect the mechanics to evolve
# into a structure that is recognized by omnibenchmark as part of the specification.
cd "$(dirname "$0")"
find ../out -name "*pcas.tsv" | xargs Rscript five-pca/pcas.tsv/validate.R
find ../out -name "*.h5ad" -not -path "*/.snakemake/*" | xargs python one-data/rawdata.h5ad/validate.py
