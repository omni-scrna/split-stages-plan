#!/usr/bin/env bash
# Derive a trimmed CI plan from the canonical benchmark_conda.yaml.
#
# The canonical plan stays the single source of truth; this computes a smaller
# view for CI smoke tests by:
#   1. swapping the one-data download module for the tiny in-repo fixture
#      (omni-data reading fixtures/1-data via the file:// handler),
#   2. registering the omni_data software environment,
#   3. keeping only the first parameter combo-group per module, and
#   4. collapsing every remaining list-valued parameter to its first element
#      (so each module runs exactly once instead of a full sweep).
#
# Usage: ci/trim-plan.sh [SRC_YAML] > benchmark_ci.yaml
set -euo pipefail

src="${1:-benchmark_conda.yaml}"
root="$(cd "$(dirname "$0")/.." && pwd)"
fixture_uri="file://${root}/fixtures/1-data"

# Pinned omni-data commit (file:// fixture loader).
omni_data_commit="eb4d368b5e83b26389e6047dd8bad6badede78f8"

fixture_module="$(
  fixture_uri="$fixture_uri" omni_data_commit="$omni_data_commit" yq -n '
    [{
      "id": "be1",
      "name": "tiny be1 fixture (CI, non-reproducible file://)",
      "software_environment": "omni_data",
      "repository": {
        "url": "https://github.com/btraven00/omni-data",
        "commit": strenv(omni_data_commit)
      },
      "parameters": [{"uri": strenv(fixture_uri)}]
    }]'
)"

FIXTURE_MODULE="$fixture_module" yq '
  (.stages[] | select(.id == "one-data").modules) = (strenv(FIXTURE_MODULE) | from_yaml)
  | .software_environments.omni_data = {"name": "omni-data fixture loader", "conda": "envs/omni-data.yml"}
  | (.stages[].modules[] | select(has("parameters")) | .parameters) |= [.[0]]
  | (.stages[].modules[] | select(has("parameters")) | .parameters[][] | select(tag == "!!seq")) |= .[0]
' "$src"

# NOTE: the canonical plan is api_version 0.4.0, which matches the pinned module
# commits (omnibenchmark passes --name=<dataset>, and modules build output
# filenames as "{name}_<suffix>"). Under api 0.5 --name becomes the module id and
# these modules would misname their outputs. Migrate the modules before bumping.
