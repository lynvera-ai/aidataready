import os

import pytest
from sqlalchemy import create_engine, text

from lynvera_aidataready import Assessment, Status
from lynvera_aidataready.config import Config

pytestmark = pytest.mark.postgres


@pytest.fixture
def database(monkeypatch):
    url = os.environ.get("AIDATAREADY_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set AIDATAREADY_TEST_DATABASE_URL to a disposable PostgreSQL database.")
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS aidataready_test"))
        connection.execute(text("DROP TABLE IF EXISTS aidataready_test.documents"))
        connection.execute(text("CREATE TABLE aidataready_test.documents (id int, content text)"))
        connection.execute(
            text("INSERT INTO aidataready_test.documents VALUES (:id, :content)"),
            [{"id": i, "content": "safe"} for i in range(11)],
        )
    monkeypatch.setenv("AIDATAREADY_DATABASE_URL", url)
    config = Config.model_validate(
        {
            "project": {"name": "postgres"},
            "source": {
                "type": "postgres",
                "schema_name": "aidataready_test",
                "table": "documents",
                "allowed_tables": ["documents"],
                "timeout_ms": 1000,
            },
            "limits": {"batch_size": 3},
            "rules": {"unique_fields": ["id"]},
        }
    )
    yield engine, config
    with engine.begin() as connection:
        connection.execute(text("DROP SCHEMA aidataready_test CASCADE"))
    engine.dispose()


def test_postgres_streaming_and_parameterized_filters(database):
    _, config = database
    result = Assessment(config).run()
    assert result.status == Status.PASS
    assert result.rows_examined == 11
    assert result.statistics["batches"] == 4
    config.source.filters = {"content": "safe' OR 1=1 --"}
    assert Assessment(config).run().status == Status.INCONCLUSIVE
    config.source.filters = {"id": 3}
    assert Assessment(config).run().rows_examined == 1
    config.source.filters = {}
    config.limits.max_rows = 5
    result = Assessment(config).run()
    assert not result.complete
    assert result.rows_examined == 5


def test_postgres_transaction_is_read_only(database, monkeypatch):
    engine, config = database
    from sqlalchemy import event

    from lynvera_aidataready import sources

    observed = []

    @event.listens_for(engine, "before_cursor_execute")
    def observe(connection, cursor, statement, parameters, context, executemany):
        if "FROM aidataready_test.documents" in statement:
            with connection.connection.cursor() as probe:
                probe.execute("SHOW transaction_read_only")
                assert probe.fetchone()[0] == "on"
                probe.execute("SHOW statement_timeout")
                assert probe.fetchone()[0] == "1s"
            observed.append(True)

    monkeypatch.setattr(sources, "create_engine", lambda *args, **kwargs: engine)
    assert Assessment(config).run().status == Status.PASS
    assert observed


def test_postgres_blocks_writes_from_views(database):
    engine, config = database
    with engine.begin() as connection:
        connection.execute(
            text("""CREATE FUNCTION aidataready_test.write_data()
            RETURNS integer LANGUAGE plpgsql AS $$ BEGIN
            INSERT INTO aidataready_test.documents VALUES (999, 'write'); RETURN 1;
            END $$""")
        )
        connection.execute(
            text("""CREATE VIEW aidataready_test.write_view AS
            SELECT aidataready_test.write_data() AS id""")
        )
    config.source.table = "write_view"
    config.source.allowed_tables = ["write_view"]
    assert Assessment(config).run().status == Status.ERROR
    with engine.connect() as connection:
        assert (
            connection.execute(text("SELECT count(*) FROM aidataready_test.documents")).scalar()
            == 11
        )


def test_postgres_query_timeout(database):
    engine, config = database
    with engine.begin() as connection:
        connection.execute(
            text("""CREATE VIEW aidataready_test.slow_view AS
            SELECT 1 AS id FROM pg_sleep(0.1)""")
        )
    config.source.table = "slow_view"
    config.source.allowed_tables = ["slow_view"]
    config.source.timeout_ms = 1
    assert Assessment(config).run().status == Status.ERROR


def test_postgres_missing_table_is_safe_error(database):
    _, config = database
    config.source.table = "missing"
    config.source.allowed_tables = ["missing"]
    assert Assessment(config).run().status == Status.ERROR


def test_postgres_works_with_select_only_role(database, monkeypatch):
    import secrets

    from sqlalchemy.engine import make_url
    from sqlalchemy.exc import DBAPIError

    engine, config = database
    role = "adr_reader_" + secrets.token_hex(4)
    password = secrets.token_hex(16)
    with engine.begin() as connection:
        connection.execute(text(f"CREATE ROLE {role} LOGIN"))
        statement = connection.execute(
            text(
                "SELECT format('ALTER ROLE %I PASSWORD %L', "
                "CAST(:role AS text), CAST(:password AS text))"
            ),
            {"role": role, "password": password},
        ).scalar_one()
        connection.execute(text(statement))
        connection.execute(text(f"GRANT USAGE ON SCHEMA aidataready_test TO {role}"))
        connection.execute(text(f"GRANT SELECT ON aidataready_test.documents TO {role}"))
    url = make_url(os.environ["AIDATAREADY_TEST_DATABASE_URL"]).set(
        username=role, password=password
    )
    reader = create_engine(url)
    try:
        monkeypatch.setenv("AIDATAREADY_DATABASE_URL", url.render_as_string(hide_password=False))
        assert Assessment(config).run().status == Status.PASS
        with reader.begin() as connection:
            with pytest.raises(DBAPIError, match="permission denied"):
                connection.execute(text("DELETE FROM aidataready_test.documents"))
    finally:
        reader.dispose()
        with engine.begin() as connection:
            connection.execute(text(f"REVOKE ALL ON aidataready_test.documents FROM {role}"))
            connection.execute(text(f"REVOKE ALL ON SCHEMA aidataready_test FROM {role}"))
            connection.execute(text(f"DROP ROLE {role}"))
