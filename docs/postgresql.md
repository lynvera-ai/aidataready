# PostgreSQL

Assess an existing table or view through SQLAlchemy and psycopg. The adapter
uses read-only transactions, allowed table names, bound equality filters,
streamed rows, and statement timeouts. It does not accept arbitrary SQL.

## Install the driver

From the source checkout, in the environment that runs the CLI:

```bash
python -m pip install '.[postgres]'
```

`uv sync --locked --all-extras` also includes the driver.
For a local wheel, use its actual filename with the extra:

```bash
python -m pip install './lynvera_aidataready-0.1.0-py3-none-any.whl[postgres]'
```

## Prepare a small table

This optional example creates a table and role. Run it as an administrator
in a disposable PostgreSQL database, not in production:

```sql
CREATE TABLE public.documents (id integer PRIMARY KEY, content text NOT NULL);
INSERT INTO public.documents VALUES
    (1, 'Account setup instructions.'),
    (2, 'Password reset instructions.');

CREATE ROLE aidataready_reader LOGIN;
GRANT USAGE ON SCHEMA public TO aidataready_reader;
GRANT SELECT ON public.documents TO aidataready_reader;
```

Grant CONNECT on your database if its policy requires it. Set the role's
password through your database client. In psql, `\password aidataready_reader`
prompts without placing the password in command history.
For an existing source, use a role already granted only the required reads.

## Set credentials

Replace the uppercase placeholders. On macOS or Linux:

```bash
export AIDATAREADY_DATABASE_URL='postgresql+psycopg://aidataready_reader:YOUR_PASSWORD@localhost:5432/YOUR_DATABASE'
```

On Windows PowerShell:

```powershell
$env:AIDATAREADY_DATABASE_URL = 'postgresql+psycopg://aidataready_reader:YOUR_PASSWORD@localhost:5432/YOUR_DATABASE'
```

URL-encode special characters in URL credentials. Keep the URL out of YAML,
Git, screenshots, and shared reports. The CLI does not automatically load
`.env` files. Server authentication and TLS remain your database settings.

## Configure the assessment

The supplied [contract](../examples/postgres.yaml) requires `id` and `content`
and checks ID uniqueness. Run it from the checkout:

```bash
aidataready check --config examples/postgres.yaml
```

The two-row table above returns PASS. A standalone contract can use:

```yaml
project:
  name: database-documents
source:
  type: postgres
  name: documents
  url_env: AIDATAREADY_DATABASE_URL
  schema_name: public
  table: documents
  allowed_tables: [documents]
  filters:
    id: 1
  timeout_ms: 5000
profile: general
rules:
  required_fields: [id, content]
  unique_fields: [id]
```

Remove `filters` to assess all rows within the configured limits. Filter values
are bound parameters. Names must use letters, digits, or underscores, beginning
with a letter or underscore. Each source assesses one allowed table or view.

## Understand the limits

The default statement timeout is 10 seconds. Connect timeout is in whole
seconds, with a minimum of one second. Statement timeout applies to each
statement; it is not a total assessment deadline.

The query reads at most `max_rows + 1` records to detect truncation. The extra
record is not assessed. Results have no guaranteed row order. If a row limit
is reached, increase it or filter a smaller, meaningful partition.

Independent PostgreSQL statements use the server's transaction isolation.
The adapter does not establish an atomic snapshot across sources. Read-only
transactions reject attempted writes, including writes from view functions.
They do not validate your complete database access policy.

Connection failures become ERROR findings without exposing the connection URL.
Follow [troubleshooting](troubleshooting.md) to check access privately.

## Integration tests

Tests create and remove `aidataready_test` and temporary reader roles in the
chosen database. Use a disposable database whose test administrator can create
roles. Never reuse the production URL for tests.

```bash
export AIDATAREADY_TEST_DATABASE_URL='postgresql+psycopg://TEST_ADMIN:TEST_PASSWORD@localhost:5432/TEST_DATABASE'
uv run pytest -m postgres
```

This test URL is separate from the read-only application URL. Tests cover
streaming, bound filters, truncation, timeouts, blocked writes, and a SELECT-only
role. See [validation](validation.md).
