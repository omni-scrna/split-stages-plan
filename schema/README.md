# stage schemas

The CLI contract for each stage, as data: one JSON file per stage, owned by this
benchmark.

A module should the schemas for the stages it implements (via the
boilerplate's `pull.py`) and uses the shared `cli` helpers to add them to its own
argument parser, so every module implementing a stage exposes the same flags.

- `_base.json`: args every module needs to get (`--output_dir`, `--name`).
- `<stage-id>.json`: one stage's input/output contract, named for the stage's
  `id` in the plan (e.g. `two-filter`, `six-embedding-metrics`). Every module
  implementing that stage — including language variants — shares this one file.

Each arg is `{flag, type, help?, dest?, choices?}`; `type` is one of
`path | string | integer | number`. See [`docs/stage-schemas.md`](../docs/stage-schemas.md)
for the format, and the boilerplate's
[`docs/cli.md`](https://github.com/omni-scrna/boilerplate/blob/main/docs/cli.md)
for how a module consumes these.
