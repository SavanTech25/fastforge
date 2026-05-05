import click
from pathlib import Path

def discard_entity(entity_name):
    click.echo(click.style(f"\n⚡ FastForge — discard:entity {entity_name}\n", fg="cyan", bold=True))
    
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
    entity_lower = entity_name.lower()

    files_to_delete = [
        base / "entity" / f"{entity_lower}.py",
        base / "schema" / f"{entity_lower}.py",
        base / "controller" / f"{entity_lower}.py",
        base / "router" / f"r_{entity_lower}.py",
    ]

    for f in files_to_delete:
        if f.exists():
            f.unlink()
            click.echo(click.style(f"  {'deleted':>10}  {f}", fg="red"))
        else:
            click.echo(click.style(f"  {'missing':>10}  {f}", fg="yellow"))

    # Cleanup main.py
    main_py_path = project_root / "app" / "main.py"
    if main_py_path.exists():
        content = main_py_path.read_text()
        import_statement = f"from {project_name}.router.r_{entity_lower} import r_{entity_lower}"
        include_statement = f"app.include_router(r_{entity_lower})"
        
        lines = content.split('\n')
        new_lines = [line for line in lines if import_statement not in line and include_statement not in line]
        
        if len(new_lines) != len(lines):
            main_py_path.write_text('\n'.join(new_lines))
            click.echo(click.style(f"  {'updated':>10}  {main_py_path} (removed router references)", fg="blue"))

    click.echo(click.style(f"\n✔ Entity '{entity_name}' discarded!\n", fg="green", bold=True))
