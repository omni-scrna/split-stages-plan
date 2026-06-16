# Stage schemas (the module CLI contract)

This page is for **benchmark authors**: how to write the CLI **contract** for a
stage. Each stage has a *schema* — a named, versioned list of the command-line
flags that every module implementing that stage must accept. 

For convenience, one JSON file drives the same Python and R helpers, so a
module in either language exposes the same flags.

Module authors don't need this page; to wire a stage schema into an entrypoint,
see the boilerplate's
[shared CLI helpers](https://github.com/omni-scrna/boilerplate/blob/main/docs/cli.md).

## The schema file

A stage's contract is one file, `schema/<name>.json`. The `<name>` is the module
**entrypoint** it binds to (e.g. `embedding`, `knn`) — not the plan's internal
stage id (those carry ordinal prefixes like `six-embedding-metrics`, and language
variants such as `embedding-py` / `embedding-r` share one schema). For example
`schema/embedding.json`:

```json
{
  "interface": "embedding",
  "version": "0.1.0",
  "benchmark": "omni-scrna/split-stages-plan",
  "args": [
    { "flag": "--pcas.tsv", "dest": "pcas", "type": "path", "help": "PCA TSV (embedding matrix, cell_ids as rownames)" },
    { "flag": "--rawdata.clusters_truth", "dest": "clusters_truth", "type": "path", "help": "TSV of ground-truth cluster labels (cell_id, truths)" }
  ]
}
```

Top level: `interface` (the schema's name), `version`, and an optional
`benchmark`. Each entry in `args` is one flag:

| field | required | meaning |
|---|---|---|
| `flag` | yes | the option string, e.g. `--pcas.tsv` |
| `type` | yes | `path` \| `string` \| `integer` \| `number` |
| `help` | no | help text |
| `dest` | no | attribute name (see defaulting below) |
| `choices` | no | allowed values — an enum |

Every declared arg is **required** (a run must be reproducible from its invocation
line, fully explicit, no defaults). Unknown flags are rejected by the module's
parser.

> **Terminology note.** We call these *stage schemas* (or *contracts*) in documentation;
> in the code they implement `interfaces`.

### Types

| `type` | Python | R |
|---|---|---|
| `path` | `pathlib.Path` | character |
| `string` | `str` | character |
| `integer` | `int` | integer |
| `number` | `float` | double |

`path` and `string` differ only by the Python type the entrypoint gets back (a
`Path` is handy for `open`/`mkdir`); both accept any string on the command line.

### Options (enums) — `choices`

Restrict a flag to a fixed set, exactly like `argparse` `choices`:

```json
{ "flag": "--solver", "type": "string", "choices": ["arpack", "randomized"] }
```

An out-of-set value is rejected with a clear message **before** the entrypoint's
code runs.

### `dest` — the attribute name

By default a flag becomes an attribute with leading dashes stripped and `.`/`-`
turned into `_`: `--pcas.tsv` → `args.pcas_tsv`. Set `dest` to give the entrypoint
a tidier name:

```json
{ "flag": "--normalized_selected.h5", "dest": "input_h5", "type": "path" }
```

so the entrypoint reads `args.input_h5` while the stable flag stays
`--normalized_selected.h5`.

## What's shared vs. what's the module's

Three kinds of args, by owner — only the first two are schema-driven:

| source | what it holds | who owns it | on `pull` / update |
|---|---|---|---|
| `_base.json` | universal args every module gets (`--output_dir`, `--name`) | the benchmark | overwritten |
| `<name>.json` | one stage's I/O contract | the benchmark | overwritten |
| the module's entrypoint | its method params (`--solver`, …) | the module author | never touched |

`add_base_args` reads `_base.json`; `add_stage_args(p, "<name>")` reads the stage
schema. Method parameters are **not** in any schema — the module author
hand-writes them in plain `argparse` / base R.

`schema/_base.json`:

```json
{
  "interface": "_base",
  "version": "0.1.0",
  "args": [
    { "flag": "--output_dir", "type": "path", "help": "Output directory for results" },
    { "flag": "--name", "type": "string", "help": "Module name/identifier" }
  ]
}
```

## Where these live

The schemas — both `_base.json` and each `<name>.json` — live here in this
benchmark's [`schema/`](../schema/) directory and are owned by the benchmark author. A
module vendors the ones it implements into its own `src/common/schema/` via the
boilerplate's `pull.py` script; those vendored copies are
**overwrite-on-update**: you should not edit them by hand in a module.

Each schema is versioned **independently** by its own top-level `version` field —
bump it when you change a stage's contract. There is no separate version file for
the set.
