# Technical Decision: data-quality-checks

## Stack

- Python 3.12.13 slim image pinned by OCI digest.
- Pandera 0.32.1 with Polars integration.
- Polars 1.42.1.
- Python `csv` and `Decimal` reference engine.
- JSON Schema 2020-12 for the validated-batch and benchmark evidence boundaries.
- Docker non-root UID 10001.

## Library Roles

Pandera validates exact eager DataFrame columns and types. Polars executes native vectorized predicates, partitions accepted/quarantine rows, and writes both outputs. Standard-library code owns the oracle and exact-money semantics.

Direct dependencies and the transitive environment are pinned in `constraints.lock`. The pinned build stage creates a wheelhouse; the runtime stage installs offline from those wheels and retains the application wheel for provenance.

## Rejections

- **DuckDB:** no SQL join, aggregation store, or persistence is measured.
- **Great Expectations:** suites, stores, checkpoints, and data docs exceed the claim.
- **Spark:** 100,000 local rows do not justify distributed startup.
- **Pandera exception parsing as quarantine:** framework failures do not define the stable row/reason contract.
- **API/GraphQL/gRPC:** file gating has no remote query semantics.
- **Kafka/RabbitMQ:** no stream, fan-out, or delivery guarantee.
- **Kumo/AWS:** no cloud behavior exists.

## Structural Versus Row Failure

Wrong headers/order/types and duplicate `row_id` stop the batch. Business-rule failures remain readable and enter quarantine. Accepted plus rejected count must equal input count.

## Measurement Boundary

Fixture generation and truth persistence are setup. The timed path includes CSV read, eager Pandera schema, Polars predicates, Python construction of reason IDs for rejected rows, and writes of accepted/quarantine CSVs. One 1,000-row full warm-up precedes a 100,000-row measured run.

## Security And Operations

Input cannot equal either output; outputs cannot collide. The default path has no network, credentials, database, broker, or external data. Failure writes JSON and exits nonzero. No high-cardinality monitoring labels are introduced.

## Publication Verification

The exact Pandera 0.32.1/Polars 1.42.1 API, manifest schema, parity test, Ruff, coverage, locked wheel installation, and three full benchmark runs execute in the image before publication.
