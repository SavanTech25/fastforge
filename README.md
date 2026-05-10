# ⚡ fast-stack-forge

[![PyPI version](https://badge.fury.io/py/fast-stack-forge.svg)](https://badge.fury.io/py/fast-stack-forge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

FastForge is a powerful, Symfony-style CLI scaffolder designed to bootstrap and accelerate the development of FastAPI applications. It provides a robust, production-ready directory structure, fully integrated with `uv` for lightning-fast package management, alongside essential utilities like rate limiting, scheduling, WebSocket management, and JWT middleware.

## ✨ Features

- **Rapid Scaffolding**: Generate full FastAPI projects with a single command.
- **Entity Generation**: Automatically create models, schemas, controllers, and routers for your database entities.
- **AI Service Integration**: Instantly scaffold RAG, Agentic, and OCR services powered by LLMs (OpenAI, Anthropic, Mistral, Azure).
- **dbt Support**: Built-in commands to initialize and manage analytical engineering pipelines.
- **Data Sync**: Generate ELT scripts to sync NoSQL databases (like MongoDB) to relational databases (like PostgreSQL).
- **Production-Ready**: Includes pre-configured JWT middleware, rate limiting (slowapi), background scheduling (apscheduler), and WebSockets.

## 🚀 Installation

Since FastForge manages virtual environments and dependencies via `uv`, you should install it globally using `uv tool`:

```bash
uv tool install fast-stack-forge
```

*(Alternatively, you can install from source: `uv tool install git+https://github.com/SavanTech25/fast-stack-forge.git`)*

## 🛠️ Usage

### 1. Initialize a Project

To bootstrap a new project, use the `init` command. You can specify your preferred database engine (`sqlite`, `postgresql`, `mysql`, or `mongodb`).

```bash
fast-stack-forge init my_project --db mongodb
```

This will create a structured FastAPI project that utilizes `pyproject.toml` and a `Makefile` for streamlined development.

### 2. Run the Scaffolded Project

Navigate into your generated project and install dependencies:

```bash
cd my_project
make install
source .venv/bin/activate
```

Start the development server:

```bash
make run
```

### 3. Generate Entities (Models, Schemas, Controllers, Routers)

FastForge features a `make:entity` command that automatically generates your boilerplate code for a given entity. Make sure you run this from the root of your newly created project!

```bash
fast-stack-forge make:entity User name:string age:int email:string:hash is_active:bool
```

**Field Syntax:** `name:type[:modifier]`
- **Types:** `string`, `int`, `float`, `bool`, `text`, `date`, `datetime`
- **Modifiers:** `encrypt`, `hash`, `nullable`, `fk=ModelName`

### 4. FastForge ETL (dbt Integration)

FastForge now includes native scaffolding for analytical engineering via **dbt**! 

To initialize a complete dbt project package inside your `src/` directory:

```bash
fast-stack-forge init:etl my_dbt_project --archi medallion --connector local
```
- **`--archi`**: Choose `default` (stg, int, mart), `medallion` (bronze, silver, gold), or `star` (raw, dim, fact).
- **`--connector`**: Choose `local` (DuckDB), `snowflake`, `bigquery`, or `postgres`.

To quickly scaffold a dbt model inside your project without boilerplate:

```bash
fast-stack-forge make:dbt fact_user --view --incremental --layer silver
```
- **`--view`**: Sets materialization to `view`.
- **`--incremental`**: Configures incremental logic automatically.

### 5. Generate AI Services

FastForge includes a powerful `make:service` command that instantly scaffolds production-ready AI services (RAG, Agents, OCR) connected directly to your FastAPI routes.

```bash
fast-stack-forge make:service DocumentOCR --type ocr --provider azure
```

**Options:**
- **`--type`**: Choose `rag` (Retrieval-Augmented Generation), `agent` (Tool-calling Agent), `agentic` (Workflow State Graph), or `ocr` (Vision Extraction).
- **`--provider`**: Choose `openai`, `anthropic`, `mistral`, `gemini`, or `azure`.
- **`--vector-store`**: (For `rag` type only). Choose `chroma` (Local), `qdrant` (Cloud/Docker), or `supabase` (PostgreSQL/pgvector). Defaults to `chroma`.

**Example: Building a fully-functional RAG service with Qdrant and OpenAI**
```bash
fast-stack-forge make:service HelpdeskBot --type rag --provider openai --vector-store qdrant
```
This generates the `HelpdeskBotService` integrated with `langchain-openai`, `langchain-qdrant`, and automatically exposes a `POST /helpdeskbot` endpoint with JWT authentication in your FastAPI app!

### 6. Generate Data Sync Scripts (ELT)

To support the standard dbt architecture (where your operational database needs to be replicated to your analytical database), you can use the `make:sync` command.

```bash
fast-stack-forge make:sync MongoToPg --source mongodb --dest postgres
```
This scaffolds a pure-Python sync script utilizing `pymongo`, `pandas`, and `sqlalchemy`. The generated script handles flattening NoSQL documents and automatically syncing them to PostgreSQL, with built-in `APScheduler` boilerplate for continuous execution.

## 🏗️ Architecture

When you initialize a project with FastForge, it generates a clean, modular structure. 

### Generated Directory Structure

*(Note: PyPI does not support Mermaid diagrams natively, so here is the ASCII representation of the architecture)*

```text
my_project/
├── Makefile
├── pyproject.toml
├── README.md
├── app/
│   └── main.py          <-- FastAPI entry point, imports db & limiter
└── src/
    └── my_project/
        ├── controller/  <-- Business logic
        ├── data/        <-- database.py
        ├── entity/      <-- ORM Models
        ├── middleware/  <-- middleware.py (JWTBearer)
        ├── router/      <-- API Routes
        ├── schema/      <-- Pydantic Models
        ├── service/     <-- Generated AI Services
        └── utils/
            ├── connection_manager.py
            ├── crud_router.py
            ├── limiter.py
            └── scheduling.py
```

### Explanation of Components

- **`app/main.py`**: The main FastAPI entry point. It handles lifecycle events (connecting to the database, starting schedulers) and attaches rate limiters.
- **`src/{project_name}/`**: Your primary application package, automatically recognized by `pyproject.toml` and `uv`.
  - **`entity/`**: Database models (SQLAlchemy or motor/MongoDB depending on your `init` choice).
  - **`schema/`**: Pydantic models for validation and serialization.
  - **`controller/`**: Business logic and database interaction functions.
  - **`router/`**: API route definitions, connected to your controllers.
  - **`data/`**: Database configuration and connection setup.
  - **`middleware/`**: Contains pre-configured `JWTBearer` middleware for instant authentication handling.
  - **`utils/`**:
    - `limiter.py`: Pre-configured `slowapi` rate limiting.
    - `scheduling.py`: Asynchronous background task scheduler via `apscheduler`.
    - `connection_manager.py`: Generic WebSocket manager.
    - `crud_router.py`: A generic factory for building standard CRUD routes effortlessly.

## 🤝 Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request if you have ideas for new features or improvements.

## 📄 License
This project is licensed under the MIT License.
