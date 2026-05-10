import click
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "sync"

def render(template_name, context):
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), trim_blocks=True, lstrip_blocks=True)
    return env.get_template(template_name).render(**context)

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        click.echo(click.style(f"  {'skipped':>10}  {path}  (already exists)", fg="yellow"))
        return
    path.write_text(content)
    click.echo(click.style(f"  {'created':>10}  {path}", fg="green"))

def make_sync(sync_name, source, dest):
    click.echo(click.style(f"\n⚡ FastForge — make:sync {sync_name} (source: {source}, dest: {dest})\n", fg="cyan", bold=True))

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
    project_names = [d.name for d in src_dir.iterdir() if d.is_dir() and d.name not in ("__pycache__",) and not d.name.endswith(".egg-info")]
    if not project_names:
        click.echo(click.style("✗ No project package found inside 'src/'.", fg="red"))
        raise SystemExit(1)
        
    project_name = project_names[0]
    base = src_dir / project_name
    
    ctx = {
        "project_name": project_name,
        "sync_name": sync_name,
        "sync_name_lower": sync_name.lower(),
        "source": source,
        "dest": dest
    }
    
    sync_file = base / "sync" / f"{sync_name.lower()}.py"
    write(sync_file, render("sync_python.py.j2", ctx))
    
    # Generate requirements.txt
    req_file = base / "sync" / "requirements.txt"
    req_content = "pymongo\npandas\nsqlalchemy\npsycopg2-binary\napscheduler\npython-decouple\nloguru\n"
    write(req_file, req_content)
    
    click.echo(click.style(f"\n✔ Python Sync Script '{sync_name}' generated!\n", fg="green", bold=True))
    click.echo(click.style("  ⚠ Remember to install the required dependencies:", fg="yellow"))
    click.echo(f"    cd src/{project_name}/sync && uv pip install -r requirements.txt\n")
