# Sponsor integration research — PantryTrace

Checked 19 October 2026. This report separates implemented local integration,
documented remote integration, and access that remains unavailable.

## What is verified

| Component | Current evidence | Submission implication |
|---|---|---|
| Meterless H-MEM | Actual upstream implementation vendored, pinned, and executed locally: remember, recall after a new process, feedback, provenance audit all passed | A real sponsor engine is available without API credentials |
| Zetaris | Direct REST request shape verified against the sponsor's current source; mocked adapter tests passed | The live instance, permissions, registered views, and credentials still need connecting and a real query |
| NVIDIA Nemotron | Current endpoint and model identity verified in NVIDIA's own documentation; optional client implemented | No authenticated inference has been run |
| Cursor | Event's supplied guides require actual IDE use | Files produced by this chat do not establish that Cursor was used |

## Event and rule verification

The [official event page](https://hackathon.genai.works/event/open-agent-hackathon-2026)
confirms the build opens **22 October, 00:00 UTC** and submissions close
**27 October 2026, 23:45 UTC**. In India these are **22 October, 05:30 IST**
and **28 October, 05:15 IST**. It lists the three main tracks, the Wildcard
extension track, and the same 100-point criteria as the supplied guides.

There are version differences: the public page currently says registration
closes at 23:59 UTC and judging opens 27 October; the supplied guides say
23:45 UTC and judging opens 28 October. Public cash allocations also differ.
Use the latest HackOS announcements and Official Rules to settle those details.
Submit early enough to avoid either registration cutoff.

The supplied Welcome Guide and FAQ state that pre-window work must be declared
as pre-existing, Zetaris and Meterless are required, and development must use
Cursor. Preparation produced on 19 October must be disclosed honestly. The
Wildcard track explicitly assesses new extensions to an existing project.
The user-supplied FAQ makes the Official Rules controlling when documents conflict.

## Meterless: correct product and implementation

The sponsor is the local agent context stack at
[Meterless's official site](https://meterless.ai/engines.html), which links
to [Meterless/Meterless](https://github.com/Meterless/Meterless). Its engines
include H-MEM, World Model, Markovian, and Scout Intent. It is unrelated to
billing or usage-metering APIs. The site's event date is stale (15–20 October)
compared with the official event page, so do not copy its schedule.

The [official starter README](https://github.com/Meterless/Meterless/blob/main/templates/agentathon-starter/README.md)
uses a local H-MEM reference and explicitly requires its setup step. Memory
persists on disk; the starter maps commands to mining, retrieval, audit, and
sleep services. Its generic hackathon rubric and track list differ from this
event's rules. Use it as implementation guidance, not as the judging rubric.

PantryTrace vendors the unmodified TypeScript engine and upstream package
metadata under `vendor/meterless-hmem`, with Apache-2.0 license and notice.
The pinned commit is `a3f15cee1b108c436827cdd10740fd113016e354`.
The [upstream facade](https://github.com/Meterless/Meterless/blob/a3f15cee1b108c436827cdd10740fd113016e354/engines/hmem/reference/src/index.ts)
exports `HMEM`, constructed with `persistDir` and `actor`. PantryTrace's bridge
calls the actual `add`, `query`, `feedback`, and `ledger.history` methods in a
Node subprocess. No fictitious Meterless HTTP API is used.

The [reference package](https://github.com/Meterless/Meterless/blob/a3f15cee1b108c436827cdd10740fd113016e354/engines/hmem/reference/package.json)
describes itself as minimal and deterministic. Keep one application writer:
its JSON persistence is unsuitable for uncontrolled concurrent processes.

From the project directory:

```powershell
python scripts/setup_sponsors.py
python scripts/smoke_meterless.py
```

The first command installs the pinned `tsx` runtime through `npm ci`.
The second uses disposable memory and verifies actual cross-process persistence
and create/read/feedback ledger events. The observed result was `verified: true`,
with `remote_api_calls: 0`. This verifies the local H-MEM integration only.

Optional environment overrides:

```text
METERLESS_HMEM_DIR=<absolute directory containing src/index.ts>
METERLESS_TSX_CLI=<absolute path to node_modules/tsx/dist/cli.mjs>
METERLESS_STATE_DIR=<absolute writable application memory directory>
METERLESS_NODE=<optional path to node executable>
```

The default paths point to the bundled source, installed runtime, and
`.pantrytrace/hmem`. No Meterless account or API key is required for this path.
Fixture mode remains independent of Node and never invokes the sponsor bridge.

## Zetaris: concrete connection contract

Start with the sponsor's
[current getting-started repository](https://github.com/zetaris/getting-started),
not an unrelated SQL library. It supports a supplied event instance or an
installed platform. Accounts and JDBC drivers are provided separately. The
shared event instance requires assigned team object names and permissions.
The current cookbook marks PUDL and several bulk sources as known failures;
check each recipe before selecting it.

The [connection guide](https://github.com/zetaris/getting-started/blob/main/docs/connections/README.md)
distinguishes the SQL Editor, direct REST/JDBC, and UI proxy helpers. Raw REST
and UI proxy routes differ; changing only the port does not translate one into
the other. PantryTrace implements **direct REST**.

Set actual environment variables, or load a gitignored local environment file
into the process environment:

```text
ZETARIS_REST_URL=https://<assigned-api-host>/api/v1.0
ZETARIS_ORG_ID=<assigned numeric organization id>
ZETARIS_API_KEY=<your GUI-created bearer key>
ZETARIS_ALLOWED_TABLES=<team_schema.intake_view>,<team_schema.alias_view>,<team_schema.transfer_view>
```

The [sponsor's Cursor setup guide](https://github.com/zetaris/getting-started/blob/main/docs/connections/cursor-connection.md)
says the user creates the API key in the GUI. It also explains how to fetch
the instance's fresh `/redoc/docs.yaml` using Basic username/password
authentication; that documentation endpoint does not accept the bearer key.
The raw local REST default is port 8888; the JDBC default is
`jdbc:zetaris:lightning@localhost:10000`. A supplied cloud instance may use
different hosts and ports.

The exact request below is taken from the sponsor's
[direct REST helper](https://github.com/zetaris/getting-started/blob/main/scripts/zetaris_sql.py):

```http
POST <ZETARIS_REST_URL>/sql-editor/sqls/run
Authorization: Bearer <key>
X-Org-ID: <numeric organization id>
X-Request-ID: <new UUID>
Content-Type: application/json
```

```json
{
  "queryId": "<new UUID>",
  "sql": "SELECT * FROM TEAM.intake_view",
  "source": "SqlEditor",
  "limit": 1000
}
```

The adapter requires `headers` and `data` arrays, converts each row to a
dictionary, and preserves returned strings. Domain code must explicitly
convert quantities before comparisons. It rejects unexpected dimensions,
mutating statements, arbitrary functions, joins, subqueries, and tables outside
the configured allowlist. The view registration itself belongs in the sponsor
SQL Editor or approved setup process.

The older [Zetaris REST knowledge-base article](https://kbase.zetaris.com/knowledge/rest-api)
documents login tokens and paginated queries, but its linked Postman repository
currently returns 404. Prefer the current repository and fresh instance spec.
Its old `select`/`pageLimit` example is a different endpoint shape and must not
be substituted into the current helper.

Pending access is specific: assigned API URL, numeric organization, account,
query/create permissions, team prefix, bearer key, and registered views matching
the application schemas. Those are obtained from HackOS Resources / Help
Zetaris. No live Zetaris success can be claimed until a real query and its
provenance are recorded.

## NVIDIA: a useful, optional integration

The [official NIM API reference](https://docs.api.nvidia.com/nim/reference/llm-apis)
uses `POST https://integrate.api.nvidia.com/v1/chat/completions`.
The [Nemotron 3 Super page](https://build.nvidia.com/nvidia/nemotron-3-super-120b-a12b)
currently lists a free prototype endpoint and shows the exact model ID
`nvidia/nemotron-3-super-120b-a12b`. Account access, quotas, and endpoint
availability still need confirmation when used.

Set `NVIDIA_API_KEY`; optionally override `NVIDIA_MODEL`. The adapter can send
an evidence packet for a critique of unsupported claims and missing evidence.
Its output should remain advisory: the deterministic reconciliation policy and
human approval control operational decisions. This is a design recommendation,
not a model capability guarantee. No authenticated call has yet been executed.

Do not default to the older 49B v1.5 model without checking availability: its
[current model page](https://build.nvidia.com/nvidia/llama-3_3-nemotron-super-49b-v1_5)
marks its free endpoint deprecated.

## Reproducible validation and remaining evidence

The eight focused sponsor adapter tests passed. They verify request shape,
allowlisted reads, SQL injection rejection, malformed result handling,
the official engine subprocess boundary, missing dependency messages, and
configuration reporting with no provider calls. The separate real Meterless
smoke test passed against the pinned upstream implementation.

Before submission, record a real Zetaris query against the declared views,
demonstrate memory recall changing an investigation across runs, perform and
record optional Nemotron inference if used, and document actual Cursor use.
Configuration presence is not connectivity evidence; the doctor deliberately
reports `live_verified: false` until an explicit operational check is run.
