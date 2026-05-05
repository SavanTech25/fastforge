import click
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "service"

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

def make_service(service_name, service_type, provider, vector_store="chroma"):
    click.echo(click.style(f"\n⚡ FastForge — make:service {service_name} (type: {service_type}, provider: {provider}, vector: {vector_store})\n", fg="cyan", bold=True))

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
        "service_name": service_name,
        "service_name_lower": service_name.lower(),
        "provider": provider,
        "service_type": service_type,
        "vector_store": vector_store
    }
    
    # 1. Write the service file
    service_file = base / "service" / f"{service_name.lower()}.py"
    write(service_file, render(f"{service_type}.py.j2", ctx))
    
    # 2. Write the router file
    router_file = base / "router" / f"r_{service_name.lower()}.py"
    write(router_file, render("r_service.py.j2", ctx))
    
    # 3. Update main.py
    main_py_path = project_root / "app" / "main.py"
    if main_py_path.exists():
        content = main_py_path.read_text()
        import_statement = f"from {project_name}.router.r_{service_name.lower()} import r_{service_name.lower()}"
        include_statement = f"app.include_router(r_{service_name.lower()})"
        
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

    click.echo(click.style(f"\n✔ Service '{service_name}' generated!\n", fg="green", bold=True))
    
    # Dependencies instructions
    pkgs = []
    if provider in ["openai", "azure"]:
        pkgs.append("openai")
    elif provider == "anthropic":
        pkgs.append("anthropic")
    elif provider == "mistral":
        pkgs.append("mistralai")
    elif provider == "gemini":
        pkgs.append("google-genai")
        
    if service_type in ["rag", "agentic", "agent"]:
        if "langchain" not in pkgs:
            pkgs.append("langchain")
        if provider == "openai" or provider == "azure":
            pkgs.append("langchain-openai")
        elif provider == "anthropic":
            pkgs.append("langchain-anthropic")
        elif provider == "mistral":
            pkgs.append("langchain-mistralai")
        elif provider == "gemini":
            pkgs.append("langchain-google-genai")
            
    if service_type == "agentic":
        pkgs.append("langgraph")
            
    if service_type == "rag":
        if vector_store == "chroma":
            pkgs.append("langchain-chroma")
        elif vector_store == "qdrant":
            pkgs.extend(["langchain-qdrant", "qdrant-client"])
        elif vector_store == "supabase":
            pkgs.extend(["langchain-postgres", "psycopg[binary]"])
        elif vector_store == "upstash":
            pkgs.append("upstash-vector")
            
    if pkgs:
        click.echo(click.style("  ⚠ Remember to install the required dependencies:", fg="yellow"))
        click.echo(f"    uv pip install {' '.join(pkgs)}\n")
