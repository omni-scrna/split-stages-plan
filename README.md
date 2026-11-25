# split-stages-plan

[![Open in OBEditor](https://img.shields.io/badge/open-obeditor-0078d4?style=flat)](https://omnibenchmark.github.io/obeditor?url=https://github.com/omni-scrna/split-stages-plan/blob/main/benchmark_conda.yaml)


This benchmark lays out stages for each step of an scRNA-seq pipeline

## Overview

This benchmark is aligned with the v0.8.0 API of [OmniBenchmark](https://omnibenchmark.org), a framework for automated scientific benchmarking.

## Author

- **Mark Robinson** (mark.robinson@mls.uzh.ch)

## License

This project is licensed under the MIT License.

## Getting Started

1. Install OmniBenchmark:
   ```bash
   pip install omnibenchmark  # as of Nov 2026, need 'main' branch
   ```

2. Run the benchmark:
   ```bash
   ob run --cores 4 benchmark_conda.yaml
   ```

## Run output validatoin

```bash
pixi run validate-artifacts
```

## Citation

If you use this benchmark in your research, please cite it using the information in `CITATION.cff`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
