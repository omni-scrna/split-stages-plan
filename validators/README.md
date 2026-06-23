# validators

Ad-hoc output validators, run by omnibenchmark after generating outputs.

## Convention

Drop a validator at `validators/{STAGE_ID}/{OUTPUT_ID}/validate.{py,R,sh}`.

Keys are stage id and the output id as declared in the plan (e.g. `PCA/pcas_tsv`,
`DATA/rawdata_h5ad`). omnibenchmark resolves the output id to its path template and runs
the validator against every produced file for that output.

* Each script receives a **single produced file path** as its argument.
* Signal pass/fail by **exit code**: `0` = pass, non-zero = fail. (stdout/stderr are
  captured to a per-file log.)
* All validators run in the single environment named by `validators.env` in the plan. Can reuse any, keep deps minimal.

## Running

```sh
ob validate outputs benchmark_conda.yaml           # writes out/.validation/*.json
ob describe status benchmark_conda.yaml --html     # green/red per module + log links
```

Results are written to `out/.validation/`; the status report just reads them.
Re-validate after re-running a stage with `--force`.
