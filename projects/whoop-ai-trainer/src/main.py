"""
WHOOP AI Trainer — CLI entry point.

Commands:
  brief       Generate today's full multi-specialist daily brief
  ask         Ask the master trainer a specific question
  specialist  Get a report from one specific specialist only
  history     View a previously saved brief
"""
from __future__ import annotations

import os
import sys
from datetime import date

from rich import print as rprint
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.spinner import Spinner
from rich.live import Live
from rich.text import Text
import click

from .whoop.auth import get_access_token
from .whoop.client import WhoopClient
from .tools.whoop_tools import WhoopToolExecutor
from .agents import (
    MasterTrainerAgent,
    StrengthTrainerAgent,
    FunctionalTrainerAgent,
    DoctorAgent,
    DietitianAgent,
    SleepCoachAgent,
)
from .storage.cache import save_report, load_latest_report, load_report_for_date

console = Console()

SPECIALIST_MAP = {
    "strength": ("Strength & Conditioning Coach", StrengthTrainerAgent),
    "functional": ("Functional Training Specialist", FunctionalTrainerAgent),
    "doctor": ("Health & Medical Monitor", DoctorAgent),
    "dietitian": ("Sports Dietitian", DietitianAgent),
    "sleep": ("Sleep Optimisation Coach", SleepCoachAgent),
}

AGENT_COLORS = {
    "strength": "red",
    "functional": "green",
    "doctor": "blue",
    "dietitian": "yellow",
    "sleep": "magenta",
}


def _get_client() -> WhoopClient:
    client_id = os.environ.get("WHOOP_CLIENT_ID")
    client_secret = os.environ.get("WHOOP_CLIENT_SECRET")
    if not client_id or not client_secret:
        console.print(
            "[bold red]Error:[/bold red] WHOOP_CLIENT_ID and WHOOP_CLIENT_SECRET "
            "must be set in your environment or .env file."
        )
        sys.exit(1)
    token = get_access_token(client_id, client_secret)
    return WhoopClient(token)


def _print_header():
    console.print(Panel(
        "[bold white]WHOOP AI Trainer[/bold white]\n"
        "[dim]Powered by Claude + Your WHOOP Biometrics[/dim]",
        style="bold cyan",
        padding=(1, 4),
    ))


def _spin(label: str):
    return Live(Spinner("dots", text=Text(label, style="dim")), refresh_per_second=10)


@click.group()
def cli():
    """WHOOP AI Trainer — your data-driven multidisciplinary coaching team."""
    pass


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Also print each specialist's full report.")
@click.option("--model", default="claude-opus-4-7", help="Claude model to use.")
def brief(verbose: bool, model: str):
    """Generate today's full daily brief from all 5 specialists + master synthesis."""
    _print_header()

    with _get_client() as client:
        executor = WhoopToolExecutor(client)
        trainer = MasterTrainerAgent(executor, model=model)

        console.print(Rule("[cyan]Fetching your WHOOP data and consulting your team...[/cyan]"))
        console.print()

        specialists_done: list[str] = []

        with _spin("Doctor assessing health status..."):
            pass  # Doctor runs inside daily_brief

        console.print("[dim]Running multidisciplinary analysis (this takes ~60–90 seconds)...[/dim]")

        master_brief, specialist_reports = trainer.daily_brief(verbose_specialists=verbose)

    # Save to cache
    report_path = save_report(master_brief, specialist_reports)

    console.print()
    console.print(Rule("[bold cyan]YOUR DAILY BRIEF[/bold cyan]"))
    console.print(Markdown(master_brief))
    console.print()
    console.print(f"[dim]Report saved → {report_path}[/dim]")

    if verbose:
        console.print()
        console.print(Rule("[dim]Specialist Reports[/dim]"))
        for key, (title, _) in SPECIALIST_MAP.items():
            if key in specialist_reports:
                color = AGENT_COLORS.get(key, "white")
                console.print()
                console.print(Panel(
                    Markdown(specialist_reports[key]),
                    title=f"[{color}]{title}[/{color}]",
                    border_style=color,
                ))


@cli.command()
@click.argument("question", nargs=-1, required=False)
@click.option("--model", default="claude-opus-4-7", help="Claude model to use.")
def ask(question: tuple[str, ...], model: str):
    """Ask your master trainer any question. Uses live WHOOP data to answer."""
    _print_header()

    q = " ".join(question) if question else Prompt.ask("[cyan]What's your question?[/cyan]")

    with _get_client() as client:
        executor = WhoopToolExecutor(client)
        trainer = MasterTrainerAgent(executor, model=model)

        console.print()
        console.print(Rule("[cyan]Thinking...[/cyan]"))

        answer = trainer.ask(q)

    console.print()
    console.print(Panel(Markdown(answer), title="[bold cyan]Master Trainer[/bold cyan]", border_style="cyan"))


@cli.command()
@click.argument("specialist", type=click.Choice(list(SPECIALIST_MAP.keys())))
@click.option("--model", default="claude-opus-4-7", help="Claude model to use.")
def specialist(specialist: str, model: str):
    """Get a deep-dive report from one specific specialist."""
    _print_header()

    title, AgentClass = SPECIALIST_MAP[specialist]
    color = AGENT_COLORS.get(specialist, "white")

    with _get_client() as client:
        executor = WhoopToolExecutor(client)
        agent = AgentClass(executor, model=model)

        console.print(f"[dim]Consulting your {title}...[/dim]")
        console.print()

        report = agent.brief()

    console.print(Panel(
        Markdown(report),
        title=f"[{color}]{title}[/{color}]",
        border_style=color,
    ))


@cli.command()
@click.option("--date", "target_date", default=None, help="Date in YYYY-MM-DD format. Defaults to today.")
@click.option("--specialist-key", default=None, type=click.Choice(list(SPECIALIST_MAP.keys())),
              help="Show a specific specialist's report from that date.")
def history(target_date: str | None, specialist_key: str | None):
    """View a previously saved daily brief."""
    _print_header()

    if target_date:
        report = load_report_for_date(date.fromisoformat(target_date))
        label = target_date
    else:
        report = load_latest_report()
        label = "latest"

    if not report:
        console.print(f"[yellow]No saved report found for {label}.[/yellow]")
        return

    if specialist_key:
        content = report["specialists"].get(specialist_key)
        if not content:
            console.print(f"[yellow]No {specialist_key} report in that brief.[/yellow]")
            return
        title, _ = SPECIALIST_MAP[specialist_key]
        color = AGENT_COLORS.get(specialist_key, "white")
        console.print(Panel(Markdown(content), title=f"[{color}]{title}[/{color}]", border_style=color))
    else:
        console.print(Rule(f"[cyan]Brief from {report['date']}[/cyan]"))
        console.print(Markdown(report["master"]))


@cli.command()
@click.option("--model", default="claude-opus-4-7", help="Claude model to use.")
def chat(model: str):
    """Interactive chat session with your master trainer."""
    _print_header()
    console.print("[dim]Type your question and press Enter. Type 'exit' to quit.[/dim]")
    console.print()

    with _get_client() as client:
        executor = WhoopToolExecutor(client)
        trainer = MasterTrainerAgent(executor, model=model)

        while True:
            try:
                q = Prompt.ask("[bold cyan]You[/bold cyan]")
            except (KeyboardInterrupt, EOFError):
                break

            if q.strip().lower() in ("exit", "quit", "bye"):
                console.print("[dim]Goodbye! Stay consistent.[/dim]")
                break

            console.print()
            answer = trainer.ask(q)
            console.print(Panel(Markdown(answer), title="[bold cyan]Master Trainer[/bold cyan]", border_style="cyan"))
            console.print()


def main():
    # Load .env if present
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_file):
        from dotenv import load_dotenv
        load_dotenv(env_file)
    cli()


if __name__ == "__main__":
    main()
