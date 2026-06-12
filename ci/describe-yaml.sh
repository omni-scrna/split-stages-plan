#!/usr/bin/env bash
set -euo pipefail

INPUT="${1:-benchmark_conda.yaml}"

if ! command -v yq >/dev/null 2>&1; then
  echo "Error: yq is not installed or not on PATH" >&2
  exit 1
fi

yq_version="$(yq --version 2>&1 || true)"
if [[ "$yq_version" != *"mikefarah/yq"* ]] || [[ "$yq_version" != *"version v4"* ]]; then
  echo "Error: this script requires mikefarah/yq v4.x" >&2
  echo "Found: $yq_version" >&2
  echo "Install the Go binary from mikefarah/yq, not the pip package." >&2
  exit 1
fi

if [[ ! -f "$INPUT" ]]; then
  echo "Error: input file not found: $INPUT" >&2
  exit 1
fi

if [[ "$(yq e '.stages | tag' "$INPUT" 2>/dev/null || true)" != "!!seq" ]]; then
  echo "Error: $INPUT does not appear to contain a top-level stages array" >&2
  exit 1
fi

benchmark_name="$(yq e -r '.name // "<unnamed>"' "$INPUT")"
benchmark_id="$(yq e -r '.id // "<no-id>"' "$INPUT")"
stage_count="$(yq e '.stages | length' "$INPUT")"
softenv_count="$(yq e '.software_environments | keys | length // 0' "$INPUT" 2>/dev/null || echo 0)"

printf '%s (%s) | stages=%s | software_envs=%s\n' \
  "$benchmark_name" "$benchmark_id" "$stage_count" "$softenv_count"

for ((i=0; i<stage_count; i++)); do
  stage_id="$(yq e -r ".stages[$i].id // \"<no-id>\"" "$INPUT")"
  module_count="$(yq e ".stages[$i].modules | length" "$INPUT")"
  input_count="$(yq e ".stages[$i].inputs | length // 0" "$INPUT" 2>/dev/null || echo 0)"
  output_count="$(yq e ".stages[$i].outputs | length // 0" "$INPUT" 2>/dev/null || echo 0)"

  module_bits=()
  for ((j=0; j<module_count; j++)); do
    module_id="$(yq e -r ".stages[$i].modules[$j].id // \"<no-id>\"" "$INPUT")"

    parameter_set_count=0
    has_parameters="$(yq e ".stages[$i].modules[$j] | has(\"parameters\")" "$INPUT")"

    if [[ "$has_parameters" == "true" ]]; then
      parameter_object_count="$(yq e ".stages[$i].modules[$j].parameters | length" "$INPUT")"

      for ((k=0; k<parameter_object_count; k++)); do
        combo_count=1
        key_count="$(yq e ".stages[$i].modules[$j].parameters[$k] | keys | length" "$INPUT")"

        for ((m=0; m<key_count; m++)); do
          key="$(yq e -r ".stages[$i].modules[$j].parameters[$k] | keys | .[$m]" "$INPUT")"
          tag="$(yq e -r ".stages[$i].modules[$j].parameters[$k].\"$key\" | tag" "$INPUT")"

          if [[ "$tag" == "!!seq" ]]; then
            len="$(yq e ".stages[$i].modules[$j].parameters[$k].\"$key\" | length" "$INPUT")"
            combo_count=$((combo_count * len))
          fi
        done

        parameter_set_count=$((parameter_set_count + combo_count))
      done
    fi

    module_bits+=("${module_id}:${parameter_set_count}")
  done

  detail_line=""
  if (( ${#module_bits[@]} > 0 )); then
    detail_line="${module_bits[0]}"
    for ((m=1; m<${#module_bits[@]}; m++)); do
      detail_line+=", ${module_bits[$m]}"
    done
  fi

  printf '%s: modules=%s | inputs=%s | outputs=%s \n--> %s\n' \
    "$stage_id" "$module_count" "$input_count" "$output_count" "$detail_line"
done



