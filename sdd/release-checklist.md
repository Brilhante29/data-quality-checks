# Release Checklist: data-quality-checks

- [x] Claim distinguishes structural failure, row quarantine, and detector scoring.
- [x] Architecture, stack, rejections, SOLID/LSP/DIP/KISS/YAGNI/DRY are recorded.
- [x] Deterministic truth includes input hash, row IDs, ordered reasons, and multi-rule rows.
- [x] Reference engine, path guards, policy, scoring, and fixture tests pass locally.
- [x] Pandera/Polars tests skip explicitly when unavailable instead of silently passing.
- [x] Docker is non-root, local-first, secret-free, and base-digest pinned.
- [x] Reuse-kit skills/docs/catalog/profile/component-pack patches pass kit validation.
- [ ] Exact Pandera/Polars adapter imports and parity pass in Docker.
- [ ] Ruff and at least 90% focused coverage pass in Docker.
- [ ] Transitive dependencies are frozen from the successful image.
- [ ] Three full 100,000-row results and every failure are retained.
- [ ] Summary, README opening, and `evidence_status: current` agree.
- [ ] Strict project validation passes.
- [ ] Kit is published and synchronized by exact commit.
- [ ] Desktop repository is synchronized.
- [ ] GitHub metadata/topics are set and Actions is green.
