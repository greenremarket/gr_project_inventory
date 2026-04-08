# Risk Register — Phase 0 Discovery
**Captured:** 2026-04-08T14:10:22Z

| ID | Title | Severity | Likelihood | Environments | Evidence Ref |
|----|-------|----------|------------|--------------|-------------|
| R01 | CT202 identical to CT201 — staging ops may accidentally hit prod data | CRITICAL | HIGH | CT201, CT202 | BLOCKER-01, BLOCKER-02 |
| R02 | MySQL credentials exposed in plaintext systemd unit | HIGH | CERTAIN | CT201, CT202 | BLOCKER-03 |
| R03 | Enterprise token undocumented — CI/build pipeline fails from scratch | HIGH | HIGH | All | BLOCKER-08 |
| R04 | All 3 environments dirty — no reproducible clean baseline | HIGH | CERTAIN | Local, CT201, CT202 | BLOCKER-04 |
| R05 | Local dev HEAD behind prod — risk of overwriting prod changes | HIGH | HIGH | Local vs CT201/CT202 | BLOCKER-05 |
| R06 | No local Odoo — developer cannot test in isolation from prod/staging | HIGH | CERTAIN | Local | BLOCKER-06 |
| R07 | OCA/Noviat repos unpinned — fresh build may pull incompatible HEAD | MEDIUM | MEDIUM | All | BLOCKER-09 |
| R08 | TLS cert expires 2026-06-30 — 83 days until service disruption | MEDIUM | CERTAIN | CT201, CT202 | 20_runtime_services.json |
| R09 | C: drive 3.5% free — risk of failed installs / Docker data loss | MEDIUM | HIGH | Local | BLOCKER-10 |
| R10 | wkhtmltopdf absent locally — PDF tests silently skipped | MEDIUM | CERTAIN | Local | BLOCKER-07 |
| R11 | Zero unit tests — only E2E Playwright suite requiring full live stack | MEDIUM | CERTAIN | All | BLOCKER-12 |
| R12 | Two lockfiles in dashboard repo (bun.lockb + package-lock.json) — divergent installs | LOW | MEDIUM | Local | 40_dependency_provenance.json |
| R13 | psycopg2 + psycopg2-binary both installed on CT201/CT202 — import conflict risk | LOW | LOW | CT201, CT202 | 40_dependency_provenance.json |
| R14 | awbc_db (MySQL 192.168.21.206) unknown — dependency scope unclear for containerisation | MEDIUM | UNKNOWN | CT201, CT202 | BLOCKER-03 |
| R15 | psql not in Windows PATH — manual workaround for every local DB operation | LOW | CERTAIN | Local | BLOCKER-11 |
| R16 | Zope stack present in Odoo venv — bloats container image, may cause import namespace conflicts | LOW | LOW | CT201, CT202 | 40_dependency_provenance.json |
| R17 | Python 3.11 local vs 3.10 on servers — potential CI/container compatibility issue | MEDIUM | MEDIUM | All | 40_dependency_provenance.json |
| R18 | gevent missing from local venv — multi-worker mode untestable locally | HIGH | CERTAIN | Local | 40_dependency_provenance.json |
| R19 | ebics_keys/ procedure undocumented — EBICS breaks on fresh deployment | HIGH | HIGH | CT201, CT202 | 80_phase0_inputs_summary.md |
| R20 | backup_to_cloud.sh destination unknown — restore procedure not validated | MEDIUM | UNKNOWN | CT201, CT202 | 80_phase0_inputs_summary.md |
