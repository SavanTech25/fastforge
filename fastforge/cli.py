import click
from .commands.init import init_project
from .commands.make_entity import make_entity

@click.group()
@click.version_option("1.0.0", prog_name="fastforge")
def cli():
    """⚡ FastForge — Symfony-style CLI scaffolder for FastAPI + SQLAlchemy + Jinja2"""
    pass

@cli.command("init")
@click.argument("project_name")
@click.option("--db", default="sqlite", type=click.Choice(["sqlite", "postgresql", "mysql", "mongodb"]), help="Database backend")
def init(project_name, db):
    """Initialize a new FastAPI project scaffold."""
    init_project(project_name, db)

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

def main():
    cli()

if __name__ == "__main__":
    main()
