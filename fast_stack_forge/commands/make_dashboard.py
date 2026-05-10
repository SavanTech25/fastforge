import click
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "dashboard"

def render(template_path, context):
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), trim_blocks=True, lstrip_blocks=True)
    return env.get_template(template_path).render(**context)

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        click.echo(click.style(f"  {'skipped':>10}  {path}  (already exists)", fg="yellow"))
        return
    path.write_text(content)
    click.echo(click.style(f"  {'created':>10}  {path}", fg="green"))

def make_dashboard(pages):
    click.echo(click.style(f"\n⚡ FastForge — make:dashboard\n", fg="cyan", bold=True))

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
    project_names = [d.name for d in src_dir.iterdir() if d.is_dir() and d.name not in ("__pycache__",) and not d.name.endswith(".egg-info") and not d.name.endswith("_etl")]
    etl_names = [d.name for d in src_dir.iterdir() if d.is_dir() and d.name.endswith("_etl")]
    
    if not project_names:
        click.echo(click.style("✗ No project package found inside 'src/'.", fg="red"))
        raise SystemExit(1)
        
    project_name = project_names[0]
    etl_name = etl_names[0] if etl_names else f"{project_name}_etl"
    
    # Process pages
    # Default icons and descriptions
    defaults = {
        "Atelier": {"icon": "🏗️", "desc": "Manage entities, services and dbt models."},
        "Analytics": {"icon": "📊", "desc": "Data insights and KPIs."},
        "Chatbot": {"icon": "🤖", "desc": "Chat with your knowledge base."},
    }

    page_configs = []
    
    # Always ensure Atelier is there if requested or by default
    if not pages:
        pages = ["Atelier"]
    
    # Create the pages list for the home page cards
    for i, page_name in enumerate(pages):
        # Normalize name for file
        clean_name = page_name.replace(" ", "_")
        conf = defaults.get(page_name, {"icon": "📄", "desc": f"Custom page for {page_name}"})
        
        page_configs.append({
            "name": clean_name,
            "title": page_name,
            "filename": f"{i+1}_{conf['icon']}_{page_name}.py",
            "icon": conf["icon"],
            "description": conf["desc"]
        })

    ctx = {
        "project_name": project_name,
        "etl_name": etl_name,
        "pages": page_configs
    }

    dashboard_dir = project_root / "app" / "dashboard"
    pages_dir = dashboard_dir / "pages"

    # 1. Write Accueil.py
    write(dashboard_dir / "Accueil.py", render("Accueil.py.j2", ctx))

    # 2. Write each page
    for p in page_configs:
        page_file = pages_dir / p["filename"]
        if p["title"].lower() == "atelier":
            write(page_file, render("pages/atelier.py.j2", ctx))
        else:
            write(page_file, render("pages/blank.py.j2", {"page": p}))

    # 3. Update Makefile
    makefile_path = project_root / "Makefile"
    if makefile_path.exists():
        content = makefile_path.read_text()
        if "dashboard:" not in content:
            new_target = "\ndashboard:\n\tcd app/dashboard && uv run streamlit run Accueil.py\n"
            if ".PHONY:" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith(".PHONY:"):
                        if "dashboard" not in line:
                            lines[i] = line + " dashboard"
                        break
                content = '\n'.join(lines)
            
            content += new_target
            makefile_path.write_text(content)
            click.echo(click.style(f"  {'updated':>10}  {makefile_path} (added dashboard target)", fg="blue"))

    click.echo(click.style(f"\n✔ Dashboard generated with {len(pages)} pages!\n", fg="green", bold=True))
    click.echo(click.style("  To start it:", fg="yellow"))
    click.echo("    make dashboard\n")
