# Security

Report vulnerabilities privately to felipe.castillo@lynvera.ai. Include the
version, impact, and a minimal reproduction with synthetic data. Do not open a
public issue with credentials or sensitive records.

The current 0.1 release line receives security fixes. Keep dependencies updated.
Use a PostgreSQL role with SELECT access only to the intended tables. Supply
credentials through an environment variable and keep them out of YAML.

The library runs locally and sends no telemetry. Record values are omitted from
built-in reports and source error messages. Project, source, and field names
remain visible. Optional sensitive-data detection is heuristic.

Source files and extensions must be trusted. Batch budgets are not hard process
memory limits. Large records and nested objects need upstream size controls.
