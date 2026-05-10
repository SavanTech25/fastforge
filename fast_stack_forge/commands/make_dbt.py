import click
from pathlib import Path

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        click.echo(click.style(f"  {'skipped':>10}  {path}  (already exists)", fg="yellow"))
        return
    path.write_text(content)
    click.echo(click.style(f"  {'created':>10}  {path}", fg="green"))

def make_dbt(model_name, is_view, is_incremental, is_python, layer):
    click.echo(click.style(f"\n⚡ FastForge ETL — make:dbt {model_name}\n", fg="cyan", bold=True))
    
    cwd = Path.cwd()
    project_root = None
    
    for p in [cwd, *cwd.parents]:
        if (p / "src").is_dir():
            project_root = p
            break
            
    if not project_root:
        click.echo(click.style("✗ Could not resolve project root. Are you inside a FastForge project?", fg="red"))
        raise SystemExit(1)
        
    src_dir = project_root / "src"
    dbt_project_dir = None
    for d in src_dir.iterdir():
        if d.is_dir() and (d / "dbt_project.yml").exists():
            dbt_project_dir = d
            break
            
    if not dbt_project_dir:
        click.echo(click.style("✗ Could not find a dbt project (dbt_project.yml) inside 'src/'.", fg="red"))
        raise SystemExit(1)
        
    models_dir = dbt_project_dir / "models"
    
    if not models_dir.exists():
        click.echo(click.style(f"✗ 'models' directory not found in src/{dbt_project_dir.name}. Is this a dbt project?", fg="red"))
        raise SystemExit(1)

    target_dir = models_dir
    if layer:
        target_dir = models_dir / layer
        if not target_dir.exists():
            click.echo(click.style(f"⚠ Layer '{layer}' does not exist, creating it...", fg="yellow"))
    
    if is_python:
        file_path = target_dir / f"{model_name}.py"
        mat = "incremental" if is_incremental else ("view" if is_view else "table")
        
        content = f"""def model(dbt, session):
            dbt.config(
                materialized="{mat}"
            )

            # df = dbt.ref("some_model")
            
            # return df
        """
        write(file_path, content)
    else:
        file_path = target_dir / f"{model_name}.sql"
        configs = []
        if is_incremental:
            configs.append("materialized='incremental'")
        elif is_view:
            configs.append("materialized='view'")
            
        config_block = ""
        if configs:
            config_str = ", ".join(configs)
            config_block = f"{{{{\n    config(\n        {config_str}\n    )\n}}}}\n\n"
            
        incremental_block = ""
        if is_incremental:
            incremental_block = """
                {% if is_incremental() %}
                -- this filter will only be applied on an incremental run
                where event_time > (select max(event_time) from {{ this }})
                {% endif %}
            """
        
        content = f"{config_block}with source as (\n    select * from {{{{ source('my_source', 'my_table') }}}}\n)\n\nselect * from source{incremental_block}"
        write(file_path, content)

    click.echo(click.style(f"\n✔ dbt model '{model_name}' generated!\n", fg="green", bold=True))
