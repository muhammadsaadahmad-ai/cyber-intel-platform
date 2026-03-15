# Architecture — CyberOps Platform (Capstone)

## System Overview

CyberOps Platform is an **integration layer** over three independent
cyber tools. It does not duplicate their logic — it imports their
modules, orchestrates their execution, normalises their output into
a unified event schema, and exposes everything through a single
dashboard and API.

---

## Full System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CYBEROPS PLATFORM — CAPSTONE                     │
│              Integrated Cyber Intelligence Operations               │
└─────────────────────────────────────────────────────────────────────┘

PHASE MODULES (imported, not duplicated)
─────────────────────────────────────────────────────────────────────
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│    Phase 1       │  │    Phase 2       │  │    Phase 3           │
│ osint-threat-    │  │ network-anomaly- │  │ redteam-toolkit/     │
│ intel/           │  │ detector/        │  │                      │
│                  │  │                  │  │ recon/port_mapper    │
│ scrapers/        │  │ database/        │  │ exploit_mapper/      │
│ shodan_scraper   │  │ traffic.db       │  │ cve_mapper           │
│                  │  │ alerts table     │  │ mitre_mapper         │
└────────┬─────────┘  └────────┬─────────┘  └──────────┬───────────┘
         │                     │                        │
         └─────────────────────▼────────────────────────┘
                               │
ORCHESTRATION LAYER            │
─────────────────────────────────────────────────────────────────────
                    ┌──────────▼──────────┐
                    │  ops/orchestrator   │
                    │                     │
                    │ run_osint_module()  │
                    │ run_anomaly_module()│
                    │ run_recon_module()  │
                    │ _log_event()        │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Unified DB         │
                    │  database/          │
                    │  unified_models.py  │
                    │                     │
                    │  PlatformEvent      │
                    │  ThreatHunt         │
                    │  TabletopSession    │
                    └──────┬──────┬───────┘
                           │      │
INTELLIGENCE LAYER         │      │
─────────────────────────────────────────────────────────────────────
              ┌────────────▼─┐  ┌─▼──────────────┐
              │ ops/threat_  │  │ ops/tabletop.py │
              │ hunter.py    │  │                 │
              │              │  │ 4 scenarios     │
              │ 4 hypotheses │  │ Attack phases   │
              │ Cross-phase  │  │ MITRE mapping   │
              │ correlation  │  │ Q&A session     │
              └────────┬─────┘  └──────┬──────────┘
                       │               │
                       └───────┬───────┘
                               │
PRESENTATION LAYER             │
─────────────────────────────────────────────────────────────────────
                    ┌──────────▼──────────┐
                    │  dashboard4/app.py  │
                    │                     │
                    │  GET /              │
                    │  Unified HTML UI    │
                    │  port 5002          │
                    │                     │
                    │  GET /api/events    │
                    │  JSON REST feed     │
                    └─────────────────────┘
```

---

## Component Breakdown

### 1. Orchestration Layer (`ops/orchestrator.py`)

The orchestrator is the core of Phase 4. It imports Phase 1, 2, and 3
functionality using two strategies:

**Phase 1 — `importlib.util` dynamic loading:**
Phase 1's `database/models.py` conflicts with Phase 4's `database/`
package by name. Using `importlib.util.spec_from_file_location()` loads
the scraper module directly by file path, bypassing the Python module
namespace entirely. This is the correct pattern when two packages share
a directory name.

**Phase 2 — Direct SQLite query:**
Phase 2's database is read directly via SQLAlchemy with a raw SQL query.
This avoids all import conflicts by treating Phase 2's DB as a data
source rather than a Python package dependency.

**Phase 3 — sys.path injection:**
Phase 3's modules have no naming conflicts, so they are loaded via
`sys.path.insert()` and imported normally.

All findings from all three phases are normalised into `PlatformEvent`
rows via `_log_event()`, giving the dashboard a unified schema to query.

---

### 2. Unified Database (`database/unified_models.py`)

Three tables form the platform's persistent state:

```
PlatformEvent
─────────────────────────────────────────────────
id            INTEGER  PRIMARY KEY
timestamp     DATETIME Auto-set on insert
source        TEXT     phase1 / phase2 / phase3
event_type    TEXT     osint_collection / anomaly_ml / cve_finding / etc.
severity      TEXT     critical / high / medium / low / info
description   TEXT     Human-readable detail (max 490 chars)
mitre_id      TEXT     ATT&CK technique ID (e.g. T1040)
mitre_name    TEXT     ATT&CK technique name

ThreatHunt
─────────────────────────────────────────────────
id            INTEGER  PRIMARY KEY
timestamp     DATETIME Auto-set on insert
hypothesis    TEXT     Hunt hypothesis key
findings      TEXT     JSON array of matching events
status        TEXT     findings / negative
analyst_notes TEXT     Auto-generated or manual notes

TabletopSession
─────────────────────────────────────────────────
id            INTEGER  PRIMARY KEY
timestamp     DATETIME Auto-set on insert
scenario_name TEXT     Scenario title
severity      TEXT     critical / high
completed     BOOLEAN  True when all questions answered
notes         TEXT     Analyst answers to discussion questions
```

---

### 3. Threat Hunt Engine (`ops/threat_hunter.py`)

Each hunt hypothesis is defined in `config4.py` with:
- A human-readable description
- A list of target ports
- A list of context keywords

The hunt engine searches two data sources simultaneously:
- Phase 2's `alerts` table (direct DB query)
- The unified `PlatformEvent` table

A finding is recorded when either the destination port matches the
hypothesis port list, or any keyword appears in the alert description.
Results are saved to the `ThreatHunt` table and displayed as a Rich
table in the terminal.

**Available hypotheses:**

| Key | Ports | Keywords |
|---|---|---|
| `lateral_movement` | 445, 3389 | smb, rdp, pass-the-hash, psexec, wmi |
| `c2_beaconing` | 80, 443, 8080, 8443 | beacon, c2, callback, cobalt, empire |
| `data_exfiltration` | 21, 22, 53, 80, 443 | exfil, upload, dns tunnel, large transfer |
| `credential_access` | 22, 389, 636, 3306 | brute, spray, mimikatz, credential, dump |

---

### 4. Tabletop Simulator (`ops/tabletop.py`)

Four scenarios are defined in `config4.py`. Each contains:
- Scenario name and severity
- Ordered list of kill chain phases
- Associated MITRE ATT&CK technique IDs
- Five discussion questions

The simulator presents each scenario interactively in the terminal,
walks through attack phases, then poses each question to the analyst.
Answers are stored in `TabletopSession.notes` for after-action review.

This mirrors how real military and enterprise SOC teams conduct
tabletop exercises — scenario-based, structured, documented.

---

### 5. Unified Dashboard (`dashboard4/app.py`)

**Routes:**
```
GET /            → Full HTML dashboard
GET /api/events  → JSON unified event feed (latest 100)
```

**Dashboard sections:**

Phase status bar — one card per phase showing event counts and status.
Color-coded: Phase 1 green, Phase 2 blue, Phase 3 coral, Hunts purple.

Stat cards — Total events / Critical+High / Tabletop sessions /
Unique MITRE technique IDs.

Unified event feed — source badge (P1/P2/P3), event type, severity
badge, MITRE ID, timestamp. Covers all three phases in one table.

Threat hunt log — hypothesis name, FINDINGS/NEGATIVE status,
finding count, timestamp.

Runs on port 5002 — separate from Phase 1 (5000) and Phase 2 (5001)
so all three dashboards can run simultaneously.

---

## Data Flow (Full Pipeline)

```
Step 1: python3 main4.py → choose [5] full demo

Step 2: orchestrator.run_osint_module()
        └─ Loads Phase 1 shodan_scraper via importlib
        └─ Runs host lookups on research IPs
        └─ Logs each IOC as PlatformEvent (source=phase1)

Step 3: orchestrator.run_anomaly_module()
        └─ Opens Phase 2 traffic.db directly via SQLAlchemy
        └─ Reads last 20 alerts from alerts table
        └─ Logs each alert as PlatformEvent (source=phase2)

Step 4: orchestrator.run_recon_module(target)
        └─ Imports Phase 3 modules via sys.path
        └─ Runs port scan + CVE mapping + MITRE mapping
        └─ Logs each CVE finding as PlatformEvent (source=phase3)

Step 5: threat_hunter.run_hunt(hypothesis)
        └─ Searches Phase 2 DB + unified PlatformEvent table
        └─ Matches on ports and keywords
        └─ Saves ThreatHunt record (findings or negative)

Step 6: dashboard4.app runs on port 5002
        └─ Queries unified DB for all events, hunts, sessions
        └─ Renders single-pane HTML dashboard
        └─ Serves /api/events JSON endpoint
```

---

## Why This Architecture Matters

Most student portfolios show individual tools. This platform shows
**systems thinking** — the ability to design an integration layer that
normalises heterogeneous data sources into a unified intelligence picture.

That is exactly what military cyber analysts do: they don't run one tool,
they orchestrate multiple collection and detection disciplines and
synthesise the output into actionable intelligence.

This platform demonstrates that capability end to end.

---

## Security Considerations

- Each phase's database file stays in its own directory — no data mixing
- Platform DB at `database/platform.db` excluded from git
- Dashboard binds to `127.0.0.1` only — not network-exposed
- No secrets in code — all API keys loaded from `.env` in their respective phase dirs
- `importlib` loading isolates Phase 1 namespace from Phase 4

---

## Author

Muhammad Saad Ahmad — Cybersecurity Student
Portfolio: [github.com/muhammadsaadahmad-ai](https://github.com/muhammadsaadahmad-ai)
