# stage schemas

The CLI contract for each stage, as data — one JSON file per stage, owned by this
benchmark. A module vendors the schemas for the stages it implements (via the
boilerplate's `pull.py`) and uses the shared `cli` helpers to add them to its own
argument parser, so every module implementing a stage exposes the same flags.

- `_base.json` — universal args every module gets (`--output_dir`, `--name`).
- `<name>.json` — one stage's input/output contract (e.g. `embedding`, `knn`).
  The name is the module **entrypoint** it binds to, not the plan stage id.

Each arg is `{flag, type, help?, dest?, choices?}`; `type` is one of
`path | string | integer | number`. See [`docs/stage-schemas.md`](../docs/stage-schemas.md)
for the format, and the boilerplate's
[`docs/cli.md`](https://github.com/omni-scrna/boilerplate/blob/main/docs/cli.md)
for how a module consumes these.
