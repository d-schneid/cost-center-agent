# Specification: cost-center-agent

**Guidelines**: Read guidelines before executing ANY below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read project input (`product-requirements-document.md`, `intent.md`)
- [x] No Data Product ORD ID in Fit Gap Analysis → no `## Data Dependencies` section needed
- [x] Bootstrap agent code in `assets/cost-center-agent/` using sap-agent-bootstrap (invoke inside `assets/cost-center-agent/`, use copy commands — NOT files manually)
- [x] Install dependencies, validate agent starts and responds at `/.well-known/agent.json` — deferred: `sap-cloud-sdk` is internal (not public PyPI), AI Core is runtime-only; deps install in CI/CD per guidelines. Structural validation (syntax, placeholders, prebuilt tests) used instead.

---

## Runtime Skills

- [x] **No runtime skill needed.** Per guidelines-agent-skills.md, both flows (total count, top-5) are single tool-call + simple aggregation, no branching workflow or reference material. The top-5 spend caveat lives in the system prompt. A skill here would be unnecessary bloat.

---

## Project-Specific Tasks

Derived from PRD / intent. Supports two question types from Finance Controllers:
1. **Total number of cost centers** across all controlling areas
2. **Top 5 cost centers** (ranking)

### API integration (master-data-only scope — user decision)
- [x] API discovered in Step 2b: **Cost Center**, ORD ID `sap.s4:apiResource:CE_COSTCENTER_0001:v1`, OData, spec at `specification/cost-center-agent/api-specs/CE_COSTCENTER_0001.edmx`
- [x] Invoke `mcp-translation-file` skill on the EDMX spec to generate the MCP translation card. API is consumed ONLY through the generated MCP tool — NO direct HTTP/OData client in agent code.
- [x] Register the generated MCP server via `setup-solution`; add its ORD ID to `asset.yaml` `requires` (see MCP Tool Integration below)

### Agent behavior
- [x] System prompt: Finance Controller cost-center assistant. Answers (a) total cost center count, (b) top 5 cost centers. Plain language, no SAP jargon, no transaction codes.
- [x] **Count**: call MCP read tool, count returned cost centers across all controlling areas (no filter)
- [x] **Top 5 ranking**: `CE_COSTCENTER_0001` has no numeric spend field (81 props, all string/bool/date). User decision: rank by `CostCenterCreationDate` descending (5 most recently created). Agent states ranking is by creation date and that actual-spend data is unavailable from this source. Never fabricates spend.
- [x] Handle empty / auth-error responses from the MCP tool with a clear user-facing message (no stack traces)

### Scope note
- [x] Actual-spend ranking is a known ceiling: master-data API only. If true top-5-by-spend is later required, re-run API discovery and add `API_PUBSECCMTMTACTLITEM:v1`, then regenerate translation + mock.

---

## Business Instrumentation

Milestones from PRD/intent → structured logs `[MILESTONE_ID].[achieved|missed]: [description]`:
- [x] `M1.question_received` — NL question interpreted
- [x] `M2.data_retrieved` — MCP cost center tool returned data
- [x] `M3.insights_computed` — count computed / ranking resolved (or ranking-unavailable logged)
- [x] `M4.answer_delivered` — plain-language response returned
- [x] Extract business logic from `stream()` into a plain async helper (avoid `GeneratorExit` context errors) — see [guidelines-agent-python.md](../guidelines-agent-python.md)
- [x] Verify `bootstrap(app)` called and `app = server.build()` in `main.py`

---

## MCP Tool Integration

Read [guidelines-agent-mcp.md](../guidelines-agent-mcp.md).

- [x] No Data Product ORD IDs → skip DPQuery
- [x] After `mcp-translation-file` generates the MCP asset, use `setup-solution` to create/register it
- [x] Wire MCP into bootstrap-generated `agent.py` per guidelines-agent-python.md — NEVER `sap_cloud_sdk.agentgateway`, NEVER raw HTTP to SAP APIs, NEVER a tool file doing direct API access
- [x] Add the MCP server to `asset.yaml` under `requires` (one entry, exact ORD ID from the generated asset)
- [x] After MCP assets generated, create `mcp-mock.json` via `mcp-mock-config` skill (required for tests)

---

## Testing

> See [guidelines-agent-python.md](../guidelines-agent-python.md) for Python testing setup.

- [x] `conftest.py` with `IBD_TESTING=true` and MCP mock wired
- [x] Tests in `assets/cost-center-agent/tests/`: end-to-end — count question, top-5 question (including the ranking-unavailable path), auth/empty-data error path
- [x] `pytest.ini` with ≥70% coverage threshold
- [x] Run `pytest` from `assets/cost-center-agent/` (no args) → final `test_report.json`
- [x] Verify `test_report.json` exists in `assets/cost-center-agent/`; if not, rerun pytest until it does
