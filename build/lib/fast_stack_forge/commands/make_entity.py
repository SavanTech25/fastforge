import click
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from fast_stack_forge.parser import parse_fields

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "entity"

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

def make_entity(entity_name, raw_fields, no_router=False, no_controller=False):
    click.echo(click.style(f"\n⚡ FastForge — make:entity {entity_name}\n", fg="cyan", bold=True))
    try:
        fields = parse_fields(raw_fields)
    except ValueError as e:
        click.echo(click.style(f"✗ {e}", fg="red"))
        raise SystemExit(1)

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

    db_type = "sql"
    db_file = base / "data" / "database.py"
    if db_file.exists():
        db_content = db_file.read_text()
        if "connect_to_mongo" in db_content or "motor" in db_content:
            db_type = "mongodb"

    table_name = entity_name.lower() if entity_name.lower().endswith("s") else entity_name.lower() + "s"

    ctx = {
        "project_name": project_name,
        "db_type": db_type,
        "entity_name": entity_name,
        "entity_name_lower": entity_name.lower(),
        "table_name": table_name,
        "fields": fields,
        "has_date": any(f.type == "date" for f in fields),
        "has_datetime": any(f.type == "datetime" for f in fields),
        "has_encrypt": any(f.encrypt for f in fields),
        "has_hash": any(f.hash for f in fields),
        "has_fk": any(f.foreign_key for f in fields),
    }
    
    write(base / "entity" / f"{entity_name.lower()}.py", render("model.py.j2", ctx))
    write(base / "schema" / f"{entity_name.lower()}.py", render("schema.py.j2", ctx))
    if not no_controller:
        write(base / "controller" / f"{entity_name.lower()}.py", render("controller.py.j2", ctx))
    if not no_router:
        write(base / "router" / f"r_{entity_name.lower()}.py", render("router.py.j2", ctx))
        
        main_py_path = project_root / "app" / "main.py"
        if main_py_path.exists():
            content = main_py_path.read_text()
            import_statement = f"from {project_name}.router.r_{entity_name.lower()} import r_{entity_name.lower()}"
            include_statement = f"app.include_router(r_{entity_name.lower()})"
            
            if include_statement not in content:
                lines = content.split('\n')
                last_import_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith("import ") or line.startswith("from "):
                        last_import_idx = i
                
                lines.insert(last_import_idx + 1, import_statement)
                lines.append(include_statement)
                
                main_py_path.write_text('\n'.join(lines) + '\n')
                click.echo(click.style(f"  {'updated':>10}  {main_py_path} (added router)", fg="blue"))

    click.echo(click.style(f"\n✔ Entity '{entity_name}' generated!\n", fg="green", bold=True))
    if ctx["has_encrypt"]:
        click.echo(click.style("  ⚠ Champ encrypt détecté — génère ta FERNET_KEY dans .env :", fg="yellow"))
        click.echo('    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"')
        click.echo()
    for method, path in [("GET",f"/{table_name}"),("GET",f"/{table_name}/{{id}}"),("POST",f"/{table_name}"),("PATCH",f"/{table_name}/{{id}}"),("DELETE",f"/{table_name}/{{id}}")]:
        click.echo(f"    {method:<8} {path}")
    click.echo()
