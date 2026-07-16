# References

## Primary technical sources

| Source | Use |
|---|---|
| [Pandera: data validation with Polars](https://pandera.readthedocs.io/en/stable/polars.html) | Eager structural validation and explicit LazyFrame limitation. |
| [Polars CSV](https://docs.pola.rs/api/python/stable/reference/api/polars.read_csv.html) | Typed local batch loading. |
| [Polars expressions](https://docs.pola.rs/user-guide/expressions/) | Vectorized rule predicates and partitioning. |
| [Python `decimal`](https://docs.python.org/3/library/decimal.html) | Framework-independent exact-money reference policy. |
| [JSON Schema 2020-12](https://json-schema.org/draft/2020-12) | Shared benchmark contract foundation. |

## Organization references

| Source | Reused idea |
|---|---|
| [Paulescu](https://github.com/Paulescu) | Production-oriented ML/data repository organization; no code copied. |
| [Rocketseat Education](https://github.com/rocketseat-education) | Explicit boundaries and tests; no code copied. |
| [OpenSpec](https://openspec.dev/) | Spec-driven decisions and self-challenge. |
| [AI Templates](https://aitmpl.com/) | Component-selection inspiration; local skills remain authoritative. |

DuckDB and Great Expectations were evaluated and rejected for this claim in `sdd/technical-decision.md`.
