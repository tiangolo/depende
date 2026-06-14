#!/usr/bin/env python

import os
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler

import typer

app = typer.Typer()


@app.callback()
def callback() -> None:
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = "/opt/homebrew/lib"


@app.command()
def live(dirty: bool = False) -> None:
    args = ["zensical", "serve", "--dev-addr", "127.0.0.1:8008"]
    if dirty:
        args.append("--dirty")
    subprocess.run(args, env={**os.environ, "LINENUMS": "true"}, check=True)


@app.command()
def build() -> None:
    typer.echo("Building docs")
    subprocess.run(["zensical", "build"], check=True)
    typer.secho("Successfully built docs", color=typer.colors.GREEN)


@app.command()
def serve() -> None:
    typer.echo("Warning: this is a very simple server.")
    typer.echo("For development, use the command live instead.")
    typer.echo("Make sure you run the build command first.")
    os.chdir("site")
    server = HTTPServer(("", 8008), SimpleHTTPRequestHandler)
    typer.echo("Serving at: http://127.0.0.1:8008")
    server.serve_forever()


if __name__ == "__main__":
    app()
