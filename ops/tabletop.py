import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config4 import TABLETOP_SCENARIOS
from database.unified_models import Session, TabletopSession
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def list_scenarios():
    console.print("\n[bold cyan]Available tabletop scenarios:[/bold cyan]")
    for s in TABLETOP_SCENARIOS:
        sev_color = "red" if s["severity"] == "critical" else "yellow"
        console.print(
            f"  [{sev_color}][{s['id']}][/{sev_color}] "
            f"{s['name']:<25} severity: {s['severity']}"
        )

def run_scenario(scenario_id):
    """Run an interactive tabletop exercise."""
    scenario = next((s for s in TABLETOP_SCENARIOS
                     if s["id"] == scenario_id), None)
    if not scenario:
        console.print(f"[red][-] Scenario {scenario_id} not found.[/red]")
        return

    console.print(Panel.fit(
        f"[bold red]{scenario['name'].upper()}[/bold red]\n"
        f"[dim]Severity: {scenario['severity']} | "
        f"MITRE techniques: {', '.join(scenario['mitre'])}[/dim]",
        border_style="red",
        title="TABLETOP EXERCISE"
    ))

    # Show attack phases
    console.print("\n[bold yellow]Attack phases:[/bold yellow]")
    for i, phase in enumerate(scenario["phases"], 1):
        console.print(f"  {i}. {phase}")

    # Interactive Q&A
    console.print("\n[bold cyan]Discussion questions:[/bold cyan]")
    console.print("[dim]Answer each question. Press Enter to skip.[/dim]\n")

    notes = []
    for i, question in enumerate(scenario["questions"], 1):
        console.print(f"[yellow]Q{i}:[/yellow] {question}")
        answer = input("   Your answer: ").strip()
        if answer:
            notes.append(f"Q{i}: {question}\nA: {answer}")
        console.print()

    # Save session
    session = Session()
    ts = TabletopSession(
        scenario_name = scenario["name"],
        severity      = scenario["severity"],
        completed     = True,
        notes         = "\n\n".join(notes)
    )
    session.add(ts)
    session.commit()
    session.close()

    console.print(Panel.fit(
        f"[green]Exercise complete: {scenario['name']}[/green]\n"
        f"[dim]{len(notes)} questions answered. Session saved.[/dim]",
        border_style="green"
    ))
