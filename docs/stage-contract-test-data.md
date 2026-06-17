# Stage Contract Test Data

When someone changes a module, we want a quick way to check its output still
looks right — without re-running the whole benchmark on the full dataset.

A fixture run already produces real outputs for every stage. We keep one of them
per output as a **reference** (for now, the first; later we can pick — "bless" — a
preferred one). That set of references is the **contract**: an example of what
each stage's output should look like. A module can check itself against it.

## What gets built

[`ci/build-fixture-bundle.py`](../ci/build-fixture-bundle.py) gathers the
references into a small bundle:

```
by-id/<output-id>   the reference file for each stage output (e.g. by-id/pcas.tsv)
manifest.json       each output's checksum and which module produced it, plus provenance
```

```json
{
  "provenance": {
    "note": "structural fixtures from one tiny dataset on one CI run; not a reproducible result",
    "dataset": "be1",
    "plan_commit": "e3542e6",
    "run_url": "https://github.com/omni-scrna/split-stages-plan/actions/runs/…",
    "ob_version": "0.5.1.post1+g3e46b0978"
  },
  "api_version": "0.4.0",
  "outputs": {
    "pcas.tsv": { "sha256": "…", "producer": "five-pca/pca-scanpy/.../be1_pcas.tsv" }
  }
}
```

## Where and when it's published

Published as a **GitHub Release on this repo** (`omni-scrna/split-stages-plan`) —
a stable link that doesn't expire, unlike CI artifacts. It's published **only
from `main`, and only after the fixture run has passed**, so the references always
come from code that works.

```
https://github.com/omni-scrna/split-stages-plan/releases/download/contract-fixtures/bundle.tar.gz
```

## How a module uses it

Download the bundle, feed your module the reference inputs it needs, run it, and
check the outputs with this plan's validators. No full benchmark, no big dataset.

This is intended mainly for having automated actions in the CI that check if the output of a module
conform to the general I/O contract of a given stage.
