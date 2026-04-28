import click
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "dbt"

def render(template_name, context):
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), trim_blocks=True, lstrip_blocks=True)
    return env.get_template(template_name).render(**context)

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    click.echo(f"  {'created':>10}  {path}")

def init_etl_project(project_name, archi, connector):
    base = Path("src") / project_name
    if base.exists():
        click.echo(click.style(f"✗ '{project_name}' already exists in src/.", fg="red"))
        raise SystemExit(1)

    click.echo(click.style(f"\n⚡ FastForge ETL — initializing dbt project '{project_name}'\n", fg="cyan", bold=True))
    
    ctx = {
        "project_name": project_name,
        "archi": archi,
        "connector": connector
    }

    # Core files
    write(base / "dbt_project.yml", render("dbt_project.yml.j2", ctx))
    write(base / "profiles.yml", render("profiles.yml.j2", ctx))
    write(base / "packages.yml", render("packages.yml.j2", ctx))
    write(base / "README.md", render("README.md.j2", ctx))
    
    # Architecture folders
    layers = []
    if archi == "medallion":
        layers = ["bronze", "silver", "gold"]
    elif archi == "star":
        layers = ["raw", "dim", "fact"]
    else:
        layers = ["stg", "int", "mart"]
        
    for layer in layers:
        (base / "models" / layer).mkdir(parents=True, exist_ok=True)
        write(base / "models" / layer / ".gitkeep", "")

    # Write boilerplate examples
    write(base / "models" / "schema.yml", render("schema.yml.j2", ctx))
    write(base / "models" / "exposures.yml", render("exposures.yml.j2", ctx))
    write(base / "snapshots" / "example_snapshot.sql", render("example_snapshot.sql.j2", ctx))
    write(base / "seeds" / "example_seed.csv", render("example_seed.csv.j2", ctx))
    
    write(base / "models" / layers[1] / "example_python_model.py", render("example_python_model.py.j2", ctx))
    
    for d in ["macros", "analyses", "tests"]:
        (base / d).mkdir(parents=True, exist_ok=True)
        write(base / d / ".gitkeep", "")

    click.echo(click.style(f"\n✔ dbt Project '{project_name}' created in src/{project_name}!\n", fg="green", bold=True))
    click.echo(f"  cd src/{project_name}")
    if connector == "local":
        click.echo(f"  uv pip install dbt-duckdb")
    elif connector == "snowflake":
        click.echo(f"  uv pip install dbt-snowflake")
    elif connector == "bigquery":
        click.echo(f"  uv pip install dbt-bigquery")
    elif connector == "postgres":
        click.echo(f"  uv pip install dbt-postgres")
        
    click.echo(f"  dbt deps")
    click.echo(f"  dbt run\n")
