# Vendored data files in `notebooks/contrib-dev/`

Provenance for third-party data committed to this directory. Anything added here that did not
originate with a student contribution belongs in this table.

---

## `ReferenceModel.dat`

Used by `vehicle_routing.ipynb` (cell 23, `model.create_instance('ReferenceModel.dat')`) for the
stochastic vehicle-routing extension. Cited in that notebook's own References section.

| | |
| --- | --- |
| **Upstream URL** | <https://raw.githubusercontent.com/Pyomo/pyomo-model-libraries/main/pysp/vehicle_routing/3-7b/ReferenceModel.dat> |
| **Browsable path** | <https://github.com/Pyomo/pyomo-model-libraries/tree/main/pysp/vehicle_routing/3-7b> |
| **Retrieved** | 2026-08-18 |
| **Size / SHA-256** | 4557 bytes · `941e5f3c2da6474ee4cc8edcc2fe6de6f9e04b32cc1b55d784722f64e36522c4` |
| **Upstream licence** | **BSD 3-Clause**, Copyright (c) 2008-2026 National Technology and Engineering Solutions of Sandia, LLC (Contract DE-NA0003525). See <https://github.com/Pyomo/pyomo-model-libraries/blob/main/LICENSE.md> |
| **Redistribution** | Permitted. Clause 1 requires the copyright notice and disclaimer be retained — satisfied by this record. |

⚠ **On the "NOASSERTION" label.** The GitHub API reports `spdx_id: NOASSERTION` for
`Pyomo/pyomo-model-libraries`. That is a *detection* failure, not an absence of licence: the repo
ships its terms as `LICENSE.md` opening with a `LICENSE\n=======` heading, which GitHub's licensee
classifier does not match. The text itself is verbatim BSD 3-Clause, identical in substance to
Pyomo's own. Redistribution here is on solid footing; the earlier hesitation recorded in
`claude/notebook_execution_audit.md` (§"Four corrections", item 2) was based on the API label alone.

### Why this file sits beside the notebook and not in `notebooks/data/`

`scripts/process_notebooks.py` rewrites any `./data/` or `../data/` string in a code cell into a
`raw.githubusercontent.com` URL when generating the published copy. That is correct for `pandas.read_csv`,
which accepts a URL — but `create_instance()` opens a **local path** and cannot read a URL, so routing
this file through `notebooks/data/` would publish a notebook that fails on the live site.

Keeping the bare filename `ReferenceModel.dat` means the path is left untouched by the rewrite, so the
file is committed to **both** `notebooks/contrib-dev/` and `notebooks/contrib/`. This matches the
existing precedent for `Dataset.csv` and `train.csv` in this directory. Do not "tidy" it into
`notebooks/data/` without first changing how the notebook loads it.
