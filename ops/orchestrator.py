import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config4 import PHASE1_DIR, PHASE2_DIR, PHASE3_DIR
from database.unified_models import Session, PlatformEvent
from rich.console import Console

console = Console()

def run_osint_module(shodan_query="apache"):
    console.print("[cyan][*] Running Phase 1 — OSINT collection...[/cyan]")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "shodan_scraper",
            os.path.expanduser("~/osint-threat-intel/scrapers/shodan_scraper.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        count = mod.search_shodan(shodan_query)
        _log_event("phase1", "osint_collection", "info",
                   f"Shodan scan complete: {count} IOCs collected",
                   "T1596", "Search Open Technical Databases")
        console.print(f"[green][+] Phase 1 complete: {count} IOCs[/green]")
        return count
    except Exception as e:
        console.print(f"[yellow][!] Phase 1 error: {e}[/yellow]")
        return 0

def run_anomaly_module():
    console.print("[cyan][*] Running Phase 2 — Anomaly detection...[/cyan]")
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        db_path = os.path.expanduser(
            "~/network-anomaly-detector/database/traffic.db"
        )
        if not os.path.exists(db_path):
            console.print("[yellow][!] Phase 2 DB not found — run Phase 2 first.[/yellow]")
            return 0
        engine   = create_engine(f"sqlite:///{db_path}")
        Session2 = sessionmaker(bind=engine)
        sess     = Session2()
        rows     = sess.execute(text(
            "SELECT alert_type, severity, description "
            "FROM alerts ORDER BY timestamp DESC LIMIT 20"
        )).fetchall()
        sess.close()
        for row in rows:
            _log_event("phase2", row[0], row[1],
                       (row[2] or "")[:200], "T1040", "Network Sniffing")
        console.print(f"[green][+] Phase 2 complete: {len(rows)} alerts imported[/green]")
        return len(rows)
    except Exception as e:
        console.print(f"[yellow][!] Phase 2 error: {e}[/yellow]")
        return 0

def run_recon_module(target="scanme.nmap.org"):
    console.print(f"[cyan][*] Running Phase 3 — Recon on {target}...[/cyan]")
    try:
        sys.path.insert(0, PHASE3_DIR)
        from recon.port_mapper import map_ports
        from exploit_mapper.cve_mapper import map_cves
        from exploit_mapper.mitre_mapper import map_mitre

        ports            = map_ports(target)
        cves             = map_cves(ports)
        enriched, summary = map_mitre(cves)

        for finding in enriched:
            if finding["cve_id"] != "N/A":
                _log_event(
                    "phase3", "cve_finding",
                    finding.get("severity", "medium"),
                    f"{finding['cve_id']} on port {finding['port']} "
                    f"({finding['service']}): {finding['description'][:100]}",
                    finding.get("mitre_id", "T1190"),
                    finding.get("mitre_technique", "Exploit Public-Facing Application")
                )
        console.print(f"[green][+] Phase 3 complete: {len(enriched)} CVE findings[/green]")
        return enriched
    except Exception as e:
        console.print(f"[yellow][!] Phase 3 error: {e}[/yellow]")
        return []

def _log_event(source, event_type, severity, description, mitre_id, mitre_name):
    session = Session()
    event   = PlatformEvent(
        source      = source,
        event_type  = event_type,
        severity    = severity,
        description = description[:490],
        mitre_id    = mitre_id,
        mitre_name  = mitre_name,
    )
    session.add(event)
    session.commit()
    session.close()
