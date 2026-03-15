# CyberOps Platform — Integrated Intel Center
### Cyber Intelligence Portfolio · Phase 4 of 4 · Capstone

![Python](https://img.shields.io/badge/Python-3.10+-00aaff?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-0077cc?style=flat-square&logo=flask&logoColor=white)
![MITRE ATT&CK](https://img.shields.io/badge/Framework-MITRE%20ATT%26CK-ff6600?style=flat-square)
![Phases](https://img.shields.io/badge/Integrates-Phases%201--2--3-00ff88?style=flat-square)
![Kali Linux](https://img.shields.io/badge/Platform-Kali%20Linux-268bd2?style=flat-square&logo=kalilinux&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-004a80?style=flat-square)

---

## Overview

**CyberOps Platform** is the capstone of a 4-phase cyber intelligence
portfolio. It unifies the OSINT collection engine (Phase 1), network anomaly
detector (Phase 2), and red team recon toolkit (Phase 3) into a single
integrated operations platform — with a unified event database, threat
hunting engine, tabletop exercise simulator, and a live multi-source
intelligence dashboard.

This is the kind of platform a real Security Operations Center (SOC) or
Military Cyber Unit uses to manage intelligence across multiple collection
and detection disciplines simultaneously.

> Built from scratch on Kali Linux by a cybersecurity student targeting
> a career in Army Intelligence Cyber Operations.

---

## What It Does

| Capability | Description |
|---|---|
| **Platform orchestrator** | Routes tasks across Phase 1, 2, and 3 modules from one entry point |
| **Unified event database** | All findings from all phases stored in a single SQLite DB |
| **Threat hunt engine** | 4 hypothesis-driven hunt queries against collected intelligence |
| **Tabletop simulator** | 4 interactive scenario-based exercises with MITRE ATT&CK mapping |
| **Unified dashboard** | Single-pane-of-glass view: all phases, all events, all hunts |
| **REST API** | `/api/events` returns unified JSON feed for external consumers |

---

## Live Demo Results

From capstone demonstration run on Kali Linux:

```
Total events         : 21   (across all phases)
Critical / High      : 3    (immediate action required)
Phase 2 alerts       : 17   (imported from anomaly detector)
Phase 3 CVE findings : 4    (OpenSSH x2, Apache x2)
Unique MITRE IDs     : 4    (T1040, T1083, T1190, T1592)
Threat hunts run     : 1    (c2_beaconing — negative)
```

---

## Architecture at a Glance

```
Phase 1 (OSINT)  +  Phase 2 (Anomaly)  +  Phase 3 (Red Team)
          │                │                      │
          └────────────────┼──────────────────────┘
                           │
              Platform Orchestrator
                           │
          ┌────────────────┼──────────────────────┐
          │                │                      │
    Threat Hunter    Tabletop Sim          Unified DB
          │                │                      │
          └────────────────┼──────────────────────┘
                           │
              Unified Dashboard (port 5002)
              REST API (/api/events)
```

---

## Project Structure

```
cyber-intel-platform/
│
├── ops/
│   ├── orchestrator.py     # Imports and runs Phase 1/2/3 modules
│   ├── threat_hunter.py    # Hypothesis-driven hunt engine
│   └── tabletop.py         # Interactive scenario simulator
│
├── dashboard4/
│   └── app.py              # Unified Flask dashboard + REST API
│
├── database/
│   └── unified_models.py   # PlatformEvent, ThreatHunt, TabletopSession
│
├── main4.py                # CLI menu — all operations
└── config4.py              # Phase paths, hunt queries, scenarios
```

---

## Quickstart

### 1. Prerequisites

All four phases must be cloned/present on your system:

```
~/osint-threat-intel          (Phase 1)
~/network-anomaly-detector    (Phase 2)
~/redteam-toolkit             (Phase 3)
~/cyber-intel-platform        (Phase 4 — this repo)
```

### 2. Install dependencies

```bash
pip install flask sqlalchemy rich colorama --break-system-packages
```

### 3. Run

```bash
cd ~/cyber-intel-platform
python3 main4.py
```

Menu options:
- `[1]` Run full pipeline (all 3 phases)
- `[2]` Run threat hunt
- `[3]` Run tabletop exercise
- `[4]` Launch dashboard at `http://127.0.0.1:5002`
- `[5]` Full demo (recommended)

---

## Threat Hunt Hypotheses

| Key | Description |
|---|---|
| `lateral_movement` | Detect SMB/RDP anomalies suggesting lateral movement |
| `c2_beaconing` | Detect C2 beaconing patterns on common ports |
| `data_exfiltration` | Detect potential data exfiltration via DNS/HTTP |
| `credential_access` | Detect credential harvesting attempts |

Run a hunt:
```bash
python3 main4.py
# choose [2], then type: c2_beaconing
```

---

## Tabletop Scenarios

| ID | Scenario | Severity | MITRE Techniques |
|---|---|---|---|
| 1 | Ransomware Attack | Critical | T1566, T1059, T1486, T1041 |
| 2 | APT Intrusion | High | T1592, T1190, T1071, T1041 |
| 3 | Insider Threat | High | T1078, T1083, T1074, T1048 |
| 4 | Zero-Day Exploit | Critical | T1190, T1210, T1543, T1486 |

Each scenario walks through attack phases, maps to ATT&CK techniques,
and poses discussion questions that mirror real incident response
decision-making.

---

## API Reference

### `GET /api/events`

Returns the 100 most recent unified platform events as JSON.

```json
[
  {
    "source":    "phase2",
    "type":      "anomaly_ml",
    "severity":  "medium",
    "description": "ML anomaly detected (score: -0.022)...",
    "mitre_id":  "T1040",
    "mitre_name": "Network Sniffing",
    "time":      "2026-03-16 00:43:27"
  }
]
```

---

## Complete Portfolio

| Phase | Repo | Visibility | What It Does |
|---|---|---|---|
| 1 | `osint-threat-intel` | Public | OSINT scraping, IOC extraction, MITRE tagging |
| 2 | `network-anomaly-detector` | Public | ML anomaly detection, port scan detection |
| 3 | `redteam-toolkit` | Private | Recon, CVE mapping, ATT&CK reports |
| 4 | `cyber-intel-platform` | Public | Unified capstone platform (this repo) |

---

## Legal & Ethical Notice

This platform is built for defensive security research, education, and
portfolio demonstration only. All network operations target explicitly
authorised test systems. The author does not condone illegal use of
any component of this software.

---

## Author

**Muhammad Saad Ahmad**
Cybersecurity Student · Aspiring Army Intelligence Cyber Analyst
GitHub: [@muhammadsaadahmad-ai](https://github.com/muhammadsaadahmad-ai)

---

*"Intelligence is not about collecting everything. It's about connecting everything."*
