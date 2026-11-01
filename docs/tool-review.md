# Tool review

Reviewed 2026-11-01. These tools already solve substantial validation problems.
AIDataReady focuses on local AI use-case contracts and a small report workflow.
It does not claim exclusive capabilities.

| Tool | Existing capabilities | MVP decision |
| --- | --- | --- |
| Great Expectations | Expectations, validation suites, and data documentation. | Reuse concepts; avoid its larger runtime in this small CLI. |
| Soda | SQL quality checks and data contracts. | Keep SQL access narrow. Do not add a Soda dependency. |
| Pandera | Dataframe schemas, type checks, and constraints. | Offer an optional adapter for existing schemas. |
| Evidently | Data quality, drift, model, and AI evaluation reports. | Do not duplicate statistical drift or model evaluation. |

Sources: [GX Core](https://greatexpectations.io/),
[Soda documentation](https://docs.soda.io/),
[Pandera documentation](https://pandera.readthedocs.io/en/stable/),
[Evidently](https://www.evidentlyai.com/).

GX Core and Evidently publish Apache-2.0 licenses. Pandera uses MIT.
The current Soda Core main branch uses Elastic License 2.0, which has use
restrictions; older Soda releases differ. Check the selected version before
integrating it.

Upstream licenses: [GX](https://github.com/great-expectations/great_expectations/blob/develop/LICENSE),
[Soda](https://github.com/sodadata/soda-core/blob/main/LICENSE),
[Pandera](https://github.com/unionai-oss/pandera/blob/main/LICENSE.txt),
[Evidently](https://github.com/evidentlyai/evidently/blob/main/LICENSE).

PyPI JSON lookups for lynvera-aidataready and aidataready both returned HTTP 404
on 2026-11-01. The project uses lynvera-aidataready to identify its owner.
The aidataready entry point installs and runs locally. Package and command names
must be checked again before publication; this does not reserve either name.
