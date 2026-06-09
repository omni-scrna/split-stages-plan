#!/usr/bin/env bash
set -euo pipefail

INPUT="${1:-benchmark_conda.yaml}"
OUTPUT="${2:-benchmark_minimal.yaml}"

if ! command -v yq >/dev/null 2>&1; then
  echo "Error: yq is not installed or not on PATH" >&2
  exit 1
fi

yq_version="$(yq --version 2>&1 || true)"

if [[ "$yq_version" != *"mikefarah/yq"* ]] || [[ "$yq_version" != *"version v4."* ]]; then
  echo "Error: this script requires mikefarah/yq v4.x" >&2
  echo "Found: $yq_version" >&2
  echo "Hint: pip-installed yq is a different tool and is not compatible with this script." >&2
  exit 1
fi

if [[ ! -f "$INPUT" ]]; then
  echo "Error: input file not found: $INPUT" >&2
  exit 1
fi

echo "Info: trimming $INPUT .." >&2

yq '
  .stages[].modules[].parameters? |=
    [(
      .[0]
      | with_entries(
          .value |= (
            select(tag == "!!seq") = [.[0]] // .
          )
        )
    )]
' "$INPUT" > "$OUTPUT"

echo "Wrote trimmed benchmark to: $OUTPUT"
