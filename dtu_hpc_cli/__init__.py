import typer

cli = typer.Typer()


@cli.command()
def list():
    print("list")


@cli.command()
def run():
    print("run")


@cli.command()
def submit():
    print("submit")


if __name__ == "__main__":
    cli()
