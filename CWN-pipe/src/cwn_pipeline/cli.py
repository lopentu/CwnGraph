"""CLI for CWN Pipeline."""

import pickle
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from cwn_pipeline.pipeline.loader import CsvLoader
from cwn_pipeline.pipeline.validator import CwnValidator
from cwn_pipeline.pipeline.differ import CwnDiffer
from cwn_pipeline.pipeline.transformer import CwnTransformer, IncrementalTransformer
from cwn_pipeline.pipeline.exporter import CwnExporter, CwnWebExporter

app = typer.Typer(
    name="cwn-update",
    help="Chinese WordNet (CWN) data update pipeline",
    no_args_is_help=True,
)
console = Console()


def load_base_image(path: str) -> tuple[dict, dict, dict]:
    """Load existing CWN image from .pyobj file."""
    with open(path, "rb") as f:
        data = pickle.load(f)
        if len(data) == 2:
            V, E = data
            meta = {}
        else:
            V, E, meta = data
    return V, E, meta


@app.command()
def validate(
    input_dir: str = typer.Argument(..., help="Directory containing CSV files"),
    base: Optional[str] = typer.Option(
        None, "--base", "-b", help="Path to base CWN image (.pyobj) for reference checks"
    ),
):
    """Validate CSV data files for errors and consistency."""
    input_path = Path(input_dir)
    if not input_path.is_dir():
        console.print(f"[red]Error: {input_dir} is not a directory[/red]")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Load CSV files
        progress.add_task("Loading CSV files...", total=None)
        loader = CsvLoader()
        load_result = loader.load_directory(input_path)

    # Display load summary
    console.print(Panel.fit("[bold]Load Summary[/bold]"))
    table = Table(show_header=True)
    table.add_column("Type", style="cyan")
    table.add_column("Count", justify="right")

    summary = load_result.summary()
    for key, value in summary.items():
        if key != "errors":
            table.add_row(key, str(value))
    console.print(table)

    # Display load errors
    if load_result.errors:
        console.print(f"\n[yellow]Load errors: {len(load_result.errors)}[/yellow]")
        for error in load_result.errors[:10]:
            console.print(f"  - Row {error['row']} in {error['file']}: {error['error']}")
        if len(load_result.errors) > 10:
            console.print(f"  ... and {len(load_result.errors) - 10} more")

    # Load base image if provided
    base_data = None
    if base:
        console.print(f"\n[dim]Loading base image: {base}[/dim]")
        base_data = load_base_image(base)

    # Run validation
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Validating data...", total=None)
        validator = CwnValidator(existing_data=base_data)
        validation_result = validator.validate(load_result)

    # Display validation results
    console.print(Panel.fit("[bold]Validation Results[/bold]"))

    if validation_result.is_valid:
        console.print("[green]✓ Data is valid[/green]")
    else:
        console.print("[red]✗ Validation failed[/red]")

    if validation_result.errors:
        console.print(f"\n[red]Errors ({len(validation_result.errors)}):[/red]")
        for error in validation_result.errors[:20]:
            console.print(f"  [{error['category']}] {error['message']}")
        if len(validation_result.errors) > 20:
            console.print(f"  ... and {len(validation_result.errors) - 20} more")

    if validation_result.warnings:
        console.print(f"\n[yellow]Warnings ({len(validation_result.warnings)}):[/yellow]")
        for warning in validation_result.warnings[:10]:
            console.print(f"  [{warning['category']}] {warning['message']}")
        if len(validation_result.warnings) > 10:
            console.print(f"  ... and {len(validation_result.warnings) - 10} more")


@app.command()
def diff(
    input_dir: str = typer.Argument(..., help="Directory containing CSV files"),
    base: str = typer.Option(..., "--base", "-b", help="Path to base CWN image (.pyobj)"),
    detect_deletions: bool = typer.Option(
        False, "--detect-deletions", help="Detect deleted entries"
    ),
):
    """Show differences between CSV data and existing CWN image."""
    input_path = Path(input_dir)
    if not input_path.is_dir():
        console.print(f"[red]Error: {input_dir} is not a directory[/red]")
        raise typer.Exit(1)

    # Load base image
    console.print(f"[dim]Loading base image: {base}[/dim]")
    base_data = load_base_image(base)

    # Load CSV files
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Loading CSV files...", total=None)
        loader = CsvLoader()
        load_result = loader.load_directory(input_path)

    # Calculate diff
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Calculating differences...", total=None)
        differ = CwnDiffer(base_data)
        diff_result = differ.diff(load_result, detect_deletions=detect_deletions)

    # Display results
    console.print(Panel.fit("[bold]Diff Summary[/bold]"))

    summary = diff_result.summary()
    table = Table(show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Count", justify="right")

    table.add_row("Total changes", str(summary["total_changes"]))
    table.add_row("[green]Additions[/green]", str(summary["additions"]))
    table.add_row("[yellow]Modifications[/yellow]", str(summary["modifications"]))
    table.add_row("[red]Deletions[/red]", str(summary["deletions"]))
    console.print(table)

    if summary["by_entity_type"]:
        console.print("\n[bold]By entity type:[/bold]")
        for key, count in sorted(summary["by_entity_type"].items()):
            console.print(f"  {key}: {count}")

    # Show sample changes
    if diff_result.additions[:5]:
        console.print("\n[green]Sample additions:[/green]")
        for change in diff_result.additions[:5]:
            console.print(f"  {change.describe()}")

    if diff_result.modifications[:5]:
        console.print("\n[yellow]Sample modifications:[/yellow]")
        for change in diff_result.modifications[:5]:
            console.print(f"  {change.describe()}")


@app.command()
def apply(
    input_dir: str = typer.Argument(..., help="Directory containing CSV files"),
    output: str = typer.Option(..., "--output", "-o", help="Output file path (.pyobj)"),
    base: Optional[str] = typer.Option(
        None, "--base", "-b", help="Path to base CWN image for incremental update"
    ),
    version: Optional[str] = typer.Option(
        None, "--version", "-v", help="Version string (e.g., v.2024.01.15)"
    ),
    skip_validation: bool = typer.Option(
        False, "--skip-validation", help="Skip validation step"
    ),
):
    """Apply CSV updates and generate new CWN image."""
    input_path = Path(input_dir)
    if not input_path.is_dir():
        console.print(f"[red]Error: {input_dir} is not a directory[/red]")
        raise typer.Exit(1)

    # Load CSV files
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Loading CSV files...", total=None)
        loader = CsvLoader()
        load_result = loader.load_directory(input_path)

    console.print(f"[green]Loaded {load_result.total_records} records[/green]")

    # Load base image if provided
    base_data = None
    if base:
        console.print(f"[dim]Loading base image: {base}[/dim]")
        base_data = load_base_image(base)

    # Validation
    if not skip_validation:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Validating data...", total=None)
            validator = CwnValidator(existing_data=base_data)
            validation_result = validator.validate(load_result)

        if not validation_result.is_valid:
            console.print("[red]Validation failed. Use --skip-validation to force.[/red]")
            for error in validation_result.errors[:5]:
                console.print(f"  [{error['category']}] {error['message']}")
            raise typer.Exit(1)
        console.print("[green]✓ Validation passed[/green]")

    # Transform data
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Transforming data...", total=None)

        if base_data:
            transformer = IncrementalTransformer(base_data)
            transform_result = transformer.apply_changes(load_result, version=version)
        else:
            transformer = CwnTransformer()
            transform_result = transformer.transform(load_result, version=version)

    # Export
    output_path = Path(output)
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = output_path.stem
    exporter = CwnExporter(output_dir)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Exporting...", total=None)
        pyobj_path = exporter.export_pyobj(transform_result, filename)

    # Summary
    console.print(Panel.fit("[bold]Export Complete[/bold]"))
    summary = transform_result.summary()
    console.print(f"  Version: {summary['version']}")
    console.print(f"  Nodes: {summary['total_nodes']}")
    console.print(f"  Edges: {summary['total_edges']}")
    console.print(f"  Output: {pyobj_path}")


@app.command()
def export_web(
    input_file: str = typer.Argument(..., help="Input CWN image file (.pyobj)"),
    output_dir: str = typer.Option(
        "./cwn_web", "--output", "-o", help="Output directory for web files"
    ),
    partitions: int = typer.Option(
        50, "--partitions", "-p", help="Number of data partitions"
    ),
):
    """Export CWN image to web format (for CwnWeb)."""
    # Load image
    console.print(f"[dim]Loading image: {input_file}[/dim]")
    V, E, meta = load_base_image(input_file)

    # Create TransformResult
    from cwn_pipeline.pipeline.transformer import TransformResult

    data = TransformResult(V=V, E=E, meta=meta)

    # Export
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Exporting to web format...", total=None)
        exporter = CwnWebExporter(output_dir, num_partitions=partitions)
        result = exporter.export(data)

    if result.success:
        console.print(f"[green]✓ Exported {len(result.files)} files to {output_dir}[/green]")
    else:
        console.print("[red]Export failed:[/red]")
        for error in result.errors:
            console.print(f"  {error}")


@app.command()
def info(
    input_file: str = typer.Argument(..., help="CWN image file (.pyobj)"),
):
    """Display information about a CWN image file."""
    console.print(f"[dim]Loading: {input_file}[/dim]")
    V, E, meta = load_base_image(input_file)

    console.print(Panel.fit("[bold]CWN Image Info[/bold]"))

    # Meta info
    console.print("\n[cyan]Metadata:[/cyan]")
    for key, value in meta.items():
        if not isinstance(value, (dict, list)):
            console.print(f"  {key}: {value}")

    # Node statistics
    node_types: dict[str, int] = {}
    for ndata in V.values():
        ntype = ndata.get("node_type", "unknown")
        node_types[ntype] = node_types.get(ntype, 0) + 1

    console.print("\n[cyan]Nodes:[/cyan]")
    table = Table(show_header=True)
    table.add_column("Type", style="cyan")
    table.add_column("Count", justify="right")
    for ntype, count in sorted(node_types.items()):
        table.add_row(ntype, str(count))
    table.add_row("[bold]Total[/bold]", f"[bold]{len(V)}[/bold]")
    console.print(table)

    # Edge statistics
    edge_types: dict[str, int] = {}
    for edata in E.values():
        etype = edata.get("edge_type", "unknown")
        edge_types[etype] = edge_types.get(etype, 0) + 1

    console.print("\n[cyan]Edges:[/cyan]")
    table = Table(show_header=True)
    table.add_column("Type", style="cyan")
    table.add_column("Count", justify="right")
    for etype, count in sorted(edge_types.items(), key=lambda x: -x[1]):
        table.add_row(etype, str(count))
    table.add_row("[bold]Total[/bold]", f"[bold]{len(E)}[/bold]")
    console.print(table)


if __name__ == "__main__":
    app()
