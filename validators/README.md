# validators

Ad-hoc checks on the files a stage produces. Each script is declared on the
output it checks, in `benchmark_conda.yaml`:

```yaml
outputs:
  - id: normalized_h5
    path: "{dataset}_normalized.h5"
    validators:
      - script: validators/NORM/normalized_h5/validate.py
```

* Every script receives a single file path and passes with exit 0.
* Scripts live at `STAGE/OUTPUT_ID/` (stage and output ids from the plan), by habit only: the declaration is what runs.
* Use as few dependencies as possible. Benchmarker adds them to the `validation` pixi environment in `pixi.toml`.
* `ob validate outputs benchmark_conda.yaml --out-dir out` runs them (omnibenchmark#358). Declaring validators needs `api_version: 0.8.0`; this plan is still on 0.4.0, so the bump comes first.
