import click
from .commands.init import init_project
from .commands.init_etl import init_etl_project
from .commands.make_entity import make_entity
from .commands.make_dbt import make_dbt

@click.group()
@click.version_option("1.0.0", prog_name="fastforge")
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
      fastforge make:entity User nom:string prenom:string pwd:string:hash role:string:fk=Role
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

def main():
    cli()

if __name__ == "__main__":
    main()
