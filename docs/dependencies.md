# Dependency licenses

Reviewed 2026-11-01 against uv.lock and installed distribution metadata.
Windows-only colorama was checked through its versioned PyPI metadata.
The table includes runtime, optional, development, and transitive dependencies.
Package links identify the exact reviewed versions.

Pydantic, Typer, Rich, SQLAlchemy, and PyYAML use MIT. Pandas uses BSD-3-Clause.
PyArrow uses Apache-2.0. ijson uses BSD-3-Clause and ISC. Optional Pandera uses MIT.
Optional psycopg and psycopg-binary use LGPL-3.0-only. They are separate installed
packages, not copied into this project's source or wheel. Preserve their license
files when redistributing an environment. Bundled client libraries have their own
terms. Inspect their upstream notices before redistributing binary packages.
See the [Psycopg installation guide](https://www.psycopg.org/psycopg3/docs/basic/install.html).

Development dependency pathspec uses MPL-2.0. NumPy's wheel includes additional
component licenses listed in its expression below. Keep upstream license and
notice files with any redistributed dependencies. This project does not relicense
those components. Our existing Apache-2.0 LICENSE is retained.

Build backend hatchling is MIT. The external uv tool is MIT OR Apache-2.0.
Build tool dependencies are resolved in isolation and are not part of the runtime
wheel. This inventory covers the lock graph, not every future resolver result.
Recheck wheel notices, dependency updates, and distribution terms before release.

| Package | Version | Declared license |
| --- | --- | --- |
| [annotated-doc](https://pypi.org/project/annotated-doc/0.0.5/) | 0.0.5 | MIT |
| [annotated-types](https://pypi.org/project/annotated-types/0.8.0/) | 0.8.0 | MIT |
| [build](https://pypi.org/project/build/1.6.1/) | 1.6.1 | MIT |
| [colorama](https://pypi.org/project/colorama/0.4.6/) | 0.4.6 | BSD License |
| [coverage](https://pypi.org/project/coverage/7.17.0/) | 7.17.0 | Apache-2.0 |
| [ijson](https://pypi.org/project/ijson/3.6.0/) | 3.6.0 | BSD-3-Clause AND ISC |
| [iniconfig](https://pypi.org/project/iniconfig/2.3.1/) | 2.3.1 | MIT |
| [librt](https://pypi.org/project/librt/0.16.0/) | 0.16.0 | MIT |
| [markdown-it-py](https://pypi.org/project/markdown-it-py/4.2.0/) | 4.2.0 | MIT |
| [mdurl](https://pypi.org/project/mdurl/0.1.2/) | 0.1.2 | MIT |
| [mypy](https://pypi.org/project/mypy/1.20.2/) | 1.20.2 | MIT |
| [mypy-extensions](https://pypi.org/project/mypy-extensions/1.1.0/) | 1.1.0 | MIT |
| [numpy](https://pypi.org/project/numpy/2.5.4/) | 2.5.4 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 |
| [packaging](https://pypi.org/project/packaging/26.3/) | 26.3 | Apache-2.0 OR BSD-2-Clause |
| [pandas](https://pypi.org/project/pandas/2.3.3/) | 2.3.3 | BSD-3-Clause |
| [pandas-stubs](https://pypi.org/project/pandas-stubs/2.3.3.260113/) | 2.3.3.260113 | BSD-3-Clause |
| [pandera](https://pypi.org/project/pandera/0.35.0/) | 0.35.0 | MIT |
| [pathspec](https://pypi.org/project/pathspec/1.1.1/) | 1.1.1 | MPL-2.0 |
| [pip-licenses](https://pypi.org/project/pip-licenses/5.5.5/) | 5.5.5 | MIT |
| [pluggy](https://pypi.org/project/pluggy/1.7.0/) | 1.7.0 | MIT |
| [prettytable](https://pypi.org/project/prettytable/3.18.0/) | 3.18.0 | BSD-3-Clause |
| [psycopg](https://pypi.org/project/psycopg/3.3.6/) | 3.3.6 | LGPL-3.0-only |
| [psycopg-binary](https://pypi.org/project/psycopg-binary/3.3.6/) | 3.3.6 | LGPL-3.0-only |
| [pyarrow](https://pypi.org/project/pyarrow/23.0.1/) | 23.0.1 | Apache-2.0 |
| [pydantic](https://pypi.org/project/pydantic/2.14.2/) | 2.14.2 | MIT |
| [pydantic-core](https://pypi.org/project/pydantic-core/2.50.2/) | 2.50.2 | MIT |
| [pygments](https://pypi.org/project/pygments/2.21.0/) | 2.21.0 | BSD-2-Clause |
| [pyproject-hooks](https://pypi.org/project/pyproject-hooks/1.3.3/) | 1.3.3 | MIT |
| [pytest](https://pypi.org/project/pytest/9.2.0/) | 9.2.0 | MIT |
| [pytest-cov](https://pypi.org/project/pytest-cov/7.1.0/) | 7.1.0 | MIT |
| [python-dateutil](https://pypi.org/project/python-dateutil/4.0.0/) | 4.0.0 | BSD-3-Clause |
| [pytz](https://pypi.org/project/pytz/2026.6/) | 2026.6 | MIT |
| [pyyaml](https://pypi.org/project/pyyaml/6.0.3/) | 6.0.3 | MIT |
| [rich](https://pypi.org/project/rich/14.3.4/) | 14.3.4 | MIT License |
| [ruff](https://pypi.org/project/ruff/0.17.3/) | 0.17.3 | MIT |
| [shellingham](https://pypi.org/project/shellingham/1.5.4/) | 1.5.4 | ISC |
| [sqlalchemy](https://pypi.org/project/sqlalchemy/2.1.6/) | 2.1.6 | MIT |
| [typeguard](https://pypi.org/project/typeguard/4.6.0/) | 4.6.0 | MIT |
| [typer](https://pypi.org/project/typer/0.27.3/) | 0.27.3 | MIT |
| [types-pytz](https://pypi.org/project/types-pytz/2026.6.0.20261031/) | 2026.6.0.20261031 | Apache-2.0 |
| [types-pyyaml](https://pypi.org/project/types-pyyaml/6.0.12.20261030/) | 6.0.12.20261030 | Apache-2.0 |
| [typing-extensions](https://pypi.org/project/typing-extensions/4.16.0/) | 4.16.0 | PSF-2.0 |
| [typing-inspect](https://pypi.org/project/typing-inspect/0.9.0/) | 0.9.0 | MIT |
| [typing-inspection](https://pypi.org/project/typing-inspection/0.4.4/) | 0.4.4 | MIT |
| [tzdata](https://pypi.org/project/tzdata/2026.6/) | 2026.6 | Apache-2.0 |
| [wcwidth](https://pypi.org/project/wcwidth/0.9.4/) | 0.9.4 | MIT |
