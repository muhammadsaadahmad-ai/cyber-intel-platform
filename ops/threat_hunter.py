import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config4 import THREAT_HUNT_QUERIES, PHASE2_DIR
from database.unified_models import Session, ThreatHunt, PlatformEvent
from rich.console import Console
from rich.table import Table

console = Console()

def run_hunt(hypothesis_key):
    """Run a threat hunt hypothesis against collected data."""
    if hypothesis_key not in THREAT_HUNT_QUERIES:
        console.print(f"[red][-] Unknown hypothesis: {hypothesis_key}[/red]")
        return

    hunt   = THREAT_HUNT_QUERIES[hypothesis_key]
    console.print(f"\n[cyan][*] Hunting: {hunt['description']}[/cyan]")

    findings = []

    # Search Phase 2 alerts
    try:
        sys.path.insert(0, PHASE2_DIR)
        from database.traffic_models import Session as P2S, Alert
        p2 = P2S()
        alerts = p2.query(Alert).all()
        p2.close()

        for alert in alerts:
            desc_lower = (alert.description or "").lower()
            if (alert.dst_port in hunt["ports"] or
                    any(kw in desc_lower for kw in hunt["keywords"])):
                findings.append({
                    "source":   "phase2_alert",
                    "type":     alert.alert_type,
                    "src":      alert.src_ip,
                    "detail":   alert.description[:100],
                    "severity": alert.severity
                })
    except Exception as e:
        console.print(f"[yellow][!] Phase 2 search error: {e}[/yellow]")

    # Search unified platform events
    session = Session()
    events  = session.query(PlatformEvent).all()
    for ev in events:
        desc_lower = (ev.description or "").lower()
        if any(kw in desc_lower for kw in hunt["keywords"]):
            findings.append({
                "source":   ev.source,
                "type":     ev.event_type,
                "src":      "platform",
                "detail":   ev.description[:100],
                "severity": ev.severity
            })

    # Save hunt result
    hunt_record = ThreatHunt(
        hypothesis    = hypothesis_key,
        findings      = json.dumps(findings),
        status        = "findings" if findings else "negative",
        analyst_notes = f"Automated hunt — {len(findings)} findings"
    )
    session.add(hunt_record)
    session.commit()
    session.close()

    # Display results
    if findings:
        table = Table(title=f"Hunt Results: {hypothesis_key}",
                      border_style="yellow")
        table.add_column("Source",   style="cyan",  width=15)
        table.add_column("Type",     style="white", width=20)
        table.add_column("Severity", style="red",   width=10)
        table.add_column("Detail",   style="dim",   width=40)
        for f in findings:
            table.add_row(f["source"], f["type"],
                          f["severity"], f["detail"])
        console.print(table)
    else:
        console.print(f"[green][+] Hunt complete: no findings for '{hypothesis_key}'[/green]")

    return findings

def list_hunts():
    """Show all available hunt hypotheses."""
    console.print("\n[bold cyan]Available threat hunt hypotheses:[/bold cyan]")
    for key, val in THREAT_HUNT_QUERIES.items():
        console.print(f"  [yellow]{key:<25}[/yellow] {val['description']}")
