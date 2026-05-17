import click
from fast_stack_forge.commands.init import init_project
from fast_stack_forge.commands.init_etl import init_etl_project
from fast_stack_forge.commands.make_entity import make_entity
from fast_stack_forge.commands.make_dbt import make_dbt
from fast_stack_forge.commands.make_service import make_service
from fast_stack_forge.commands.make_dashboard import make_dashboard
from fast_stack_forge.commands.init_ds_data import init_ds_data_project
from fast_stack_forge.commands.init_ds_make import init_ds_make

@click.group()
@click.version_option("1.0.0", prog_name="fast-stack-forge")
def cli():
    """⚡ FastForge - CLI scaffolder for FastAPI"""
    pass

@cli.command("init")
@click.argument("project_name")
@click.option("--db", default="sqlite", type=click.Choice(["sqlite", "postgresql", "mysql", "mongodb"]), help="Database backend")
def init(project_name, db):
    """Initialize a new FastAPI project scaffold."""
    init_project(project_name, db)

@cli.command("init:etl")
@click.argument("project_name")
@click.option("--archi", default="default", type=click.Choice(["default", "medallion", "star"]), help="Architecture style")
@click.option("--connector", default="local", type=click.Choice(["local", "snowflake", "bigquery", "postgres"]), help="Data warehouse connector")
def init_etl(project_name, archi, connector):
    """Initialize a new dbt ETL project scaffold."""
    init_etl_project(project_name, archi, connector)

@cli.command("make:entity")
@click.argument("entity_name")
@click.argument("fields", nargs=-1)
@click.option("--no-router", is_flag=True, help="Skip router generation")
@click.option("--no-controller", is_flag=True, help="Skip controller generation")
def make(entity_name, fields, no_router, no_controller):
    """
    Generate entity, schema, controller and router.

    \b
    Field syntax:  name:type[:modifier]
    Types:         string, int, float, bool, text, date, datetime
    Modifiers:     encrypt, hash, nullable, fk=ModelName

    \b
    Example:
      fast-stack-forge make:entity User nom:string prenom:string pwd:string:hash role:string:fk=Role
    """
    make_entity(entity_name, fields, no_router=no_router, no_controller=no_controller)

@cli.command("make:dbt")
@click.argument("model_name")
@click.option("--view", is_flag=True, help="Materialize as view")
@click.option("--incremental", is_flag=True, help="Materialize as incremental")
@click.option("--python", is_flag=True, help="Generate a Python model instead of SQL")
@click.option("--layer", default=None, help="Specific layer to place the model (e.g. bronze, staging)")
def make_dbt_cmd(model_name, view, incremental, python, layer):
    """
    Generate a dbt model.
    """
    make_dbt(model_name, view, incremental, python, layer)

@cli.command("make:service")
@click.argument("service_name")
@click.option("--type", "service_type", required=True, type=click.Choice(["rag", "agent", "agentic", "ocr"]), help="Type of AI service")
@click.option("--provider", required=True, type=click.Choice(["openai", "anthropic", "mistral", "gemini", "azure"]), help="AI Provider to use")
@click.option("--vector-store", default="chroma", type=click.Choice(["chroma", "qdrant", "supabase", "upstash"]), help="Vector store (RAG only)")
def make_service_cmd(service_name, service_type, provider, vector_store):
    """
    Generate an AI service (RAG, Agent, OCR, etc) and its router.
    """
    make_service(service_name, service_type, provider, vector_store)

@cli.command("make:sync")
@click.argument("sync_name")
@click.option("--source", default="mongodb", help="Source database")
@click.option("--dest", default="postgres", help="Destination database")
def make_sync_cmd(sync_name, source, dest):
    """
    Generate a database synchronization script (ELT).
    """
    from fast_stack_forge.commands.make_sync import make_sync
    make_sync(sync_name, source, dest)

@cli.command("make:discard")
@click.argument("entity_name")
def discard_entity_cmd(entity_name):
    """
    Remove entity, schema, controller and router.
    """
    from fast_stack_forge.commands.discard_entity import discard_entity
    discard_entity(entity_name)

@cli.command("make:dashboard")
@click.argument("pages", nargs=-1)
def make_dashboard_cmd(pages):
    """
    Generate a Streamlit dashboard with custom pages.
    
    Example:
      fast-stack-forge make:dashboard Atelier Analytics Chatbot
    """
    make_dashboard(pages)

@cli.command("init:ds-data")
@click.argument("package_name")
@click.option("--api/--no-api", default=False, help="Include FastAPI skeleton inside the DS project (default: no)")
@click.option("--data/--no-data", default=False, help="Include ETL data folders raw/interim/processed/external (default: no)")
def init_ds_data(package_name, api, data):
    """
    Initialize an AstroData data science project.

    \b
    Features:
      - Interactive Python version selector (latest, latest-1, latest-2)
      - Open-source license (MIT, BSD-3-Clause, Apache-2.0, GPL-3.0)
      - Optional description & author
      - Name auto-sanitized: "test of test" → "test_of_test"
      - Asks if you want a companion FastAPI project (named <name>_api)
      - Uses loguru (no log files), python-decouple for config

    \b
    Flags:
      --api     Include FastAPI files inside src/<name>/api/
      --data    Create ETL data/ folders (raw, interim, processed, external)

    \b
    Example:
      fast-stack-forge init:ds-data my_project
      fast-stack-forge init:ds-data "test of test" --api --data
    """
    init_ds_data_project(package_name, include_api=api, include_data=data)


@cli.command("init:ds-make")
@click.argument("project_dir", default=".", required=False)
def init_ds_make_cmd(project_dir):
    """
    Add FastAPI + Streamlit skeleton to an existing AstroData DS project.

    \b
    Run from the project root (or pass the path as argument).
    Detects the package name from src/ automatically.

    \b
    Example:
      cd my_project && fast-stack-forge init:ds-make
      fast-stack-forge init:ds-make ./my_project
    """
    init_ds_make(project_dir)


def main():
    cli()

if __name__ == "__main__":
    main()
