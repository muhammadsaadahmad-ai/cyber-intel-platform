from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    console.print(Panel.fit(
        "[bold blue]CyberOps Platform — Integrated Intel Center[/bold blue]\n"
        "[dim]Army Intelligence Cyber Portfolio — Phase 4 Capstone[/dim]",
        border_style="blue"
    ))

    from database.unified_models import init_db
    init_db()

    console.print("\n[bold yellow]Select operation:[/bold yellow]")
    console.print("  [1] Run full pipeline (all 3 phases)")
    console.print("  [2] Run threat hunt")
    console.print("  [3] Run tabletop exercise")
    console.print("  [4] Launch unified dashboard (port 5002)")
    console.print("  [5] Full demo (pipeline + hunt + dashboard)\n")

    choice = input("Enter choice [1-5]: ").strip()

    if choice in ["1", "5"]:
        console.print("\n[bold cyan]Running integrated pipeline...[/bold cyan]")
        from ops.orchestrator import (run_osint_module,
                                           run_anomaly_module,
                                           run_recon_module)
        run_osint_module()
        run_anomaly_module()
        target = input("\nRecon target (Enter for scanme.nmap.org): ").strip()
        run_recon_module(target or "scanme.nmap.org")

    if choice in ["2", "5"]:
        from ops.threat_hunter import list_hunts, run_hunt
        list_hunts()
        key = input("\nEnter hypothesis key: ").strip()
        if key:
            run_hunt(key)

    if choice == "3":
        from ops.tabletop import list_scenarios, run_scenario
        list_scenarios()
        try:
            sid = int(input("\nEnter scenario number [1-4]: ").strip())
            run_scenario(sid)
        except ValueError:
            console.print("[red]Invalid input.[/red]")

    if choice in ["4", "5"]:
        console.print("\n[green][+] Dashboard at http://127.0.0.1:5002[/green]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")
        from dashboard4.app import run_dashboard
        run_dashboard()

if __name__ == "__main__":
    main()
