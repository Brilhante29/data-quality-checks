# Reuse Delta: data-quality-checks

## Reusable Discoveries

| Candidate | Decision | Reason | Follow-up |
|---|---|---|---|
| generated OpenSpec-style plan | patch-now | Repeated project planning should not be recreated by hand. | Keep `tools/plan-project.ps1` in the kit. |
| article voice check | patch-now | Posts should sound consistent with README/SDD evidence. | Use `voice-check.md` before publishing articles. |
| external repo patterns | guarded-use | External repositories may improve organization and benchmark design. | Record reference and update kit before spreading the pattern. |
| validated-batch manifest v1 | validate-with-consumer | #23 and #22 need artifact identity, schema, row counts, and quality outcome without importing #26 code. | Promote to the kit after #23 consumes the contract unchanged. |

## Final Gate

- [x] Reuse improvement considered.
- [x] Local skills remain primary.
- [x] External references stay attributed and problem-driven.
