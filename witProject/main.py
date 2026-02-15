import click
from wit_engine import WitEngine

engine = WitEngine()

@click.group()
def cli():
    pass

@cli.command()
def init():
    try:
        engine.init()
        click.secho("Initialized empty WIT repository.", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")

@cli.command()
@click.argument('path')
def add(path):
    try:
        engine.add(path)
        click.echo(f"Added {path} to staging.")
    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command()
def status():
    """Displays the state of the working directory and the staging area."""
    try:
        report = engine.get_status()

        click.echo(f"--- WIT STATUS ---")
        if report["last_commit"]:
            click.echo(f"On commit: {report['last_commit']}")

        # שימוש בפונקציית העזר להדפסה (אפשר להוסיף אותה ל-main או ל-utils)
        def display_section(title, files, color):
            if files:
                click.secho(f"\n{title}:", bold=True)
                for f in files:
                    click.secho(f"    {f}", fg=color)

        display_section("Changes to be committed", report["to_be_committed"], "green")
        display_section("Changes not staged for commit", report["not_staged"], "red")
        display_section("Untracked files", report["untracked"], "yellow")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red")

@cli.command()
@click.option('--message', '-m', required=True)
def commit(message):
    cid = engine.commit(message)
    if cid:
        click.secho(f"Commit created: {cid}", fg="cyan")
    else:
        click.echo("Nothing to commit.")

if __name__ == '__main__':
    cli()