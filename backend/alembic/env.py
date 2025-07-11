import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add the 'app' directory to the system path so Alembic can find models and config
# This assumes that alembic commands are run from the 'backend' directory.
# If run from project root, sys.path.append(os.path.abspath('backend')) might be needed.
# For now, assuming execution from 'backend/' directory.
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), '')) # Adds 'backend' to sys.path

# Import your app's settings and models
# These imports should resolve correctly because 'backend' is now in sys.path
from app.config import settings # Your application's settings
from app.database import Base  # Your SQLAlchemy Base
from app.models import *       # Import all your models here

# Set the sqlalchemy.url in the Alembic config object programmatically
# This ensures Alembic uses the same database URL as your application.
# The URL might be relative like "sqlite:///./data/coder_workspace.db"
# If so, Alembic needs to know the correct base path.
# If DATABASE_URL is "sqlite:///./data/coder_workspace.db", and alembic is run from `backend/`
# it will create/look for `backend/data/coder_workspace.db`.
# Our docker-compose maps host `./data` to container `/app/data`.
# The application running in Docker at `/app` will use `/app/data/coder_workspace.db`.
# For local `alembic` commands run from `backend/`, if DATABASE_URL is `sqlite:///./data/coder_workspace.db`,
# it would point to `backend/data/coder_workspace.db`.
# To make local alembic commands (run from `backend/`) and the app (run in Docker from `/app`)
# use the *same physical file on the host* (via the volume mount), the path needs careful consideration.

# If DATABASE_URL is "sqlite:///./data/coder_workspace.db":
# - App in Docker (WORKDIR /app): sees it as /app/data/coder_workspace.db (correct via volume)
# - Local Alembic (run from backend/): sees it as backend/data/coder_workspace.db
# This means local Alembic and Docker app would use DIFFERENT db files if not careful.

# Solution: The DATABASE_URL in .env should be consistent.
# Let's assume DATABASE_URL="sqlite:///./data/coder_workspace.db" means the DB is in a 'data' folder
# *relative to the project root*.
# The backend application, when running inside Docker (WORKDIR /app), has the project's 'data'
# directory mounted at '/app/data'. So, its relative path './data/coder_workspace.db' resolves to
# '/app/data/coder_workspace.db'.
# For Alembic, when run locally from the 'backend' directory, we need to adjust the path.
# A common practice is to make the path absolute or relative to a known location.

# For simplicity with SQLite and local dev:
# We expect the .env file to be in 'backend/' and DATABASE_URL="sqlite:///./data/coder_workspace.db"
# This means the database file is expected at 'backend/data/coder_workspace.db' when alembic is run from 'backend/'.
# The Docker container maps the host's 'data/' to '/app/data/'.
# If the .env inside the container has DATABASE_URL="sqlite:///./data/coder_workspace.db",
# and the app's WORKDIR is /app, then it correctly refers to /app/data/coder_workspace.db.

# The key is that `settings.DATABASE_URL` should provide the correct URL
# from the perspective of where this env.py script is run.
# If `alembic` commands are run from the `backend` directory:
# `settings.DATABASE_URL` (which is `sqlite:///./data/coder_workspace.db` by default from .env)
# will be interpreted as relative to the `backend` directory. So, `backend/data/coder_workspace.db`.
# This aligns with the volume mount for the application: `../data` on host -> `/app/data` in container.
# The application uses `sqlite:///./data/coder_workspace.db` relative to `/app`, so `/app/data/coder_workspace.db`.
# This setup means the DB file is expected at `backend/data/coder_workspace.db` on the host.
# And the `data` volume in docker-compose should be `./backend/data:/app/data` if we want this.
# OR, if we want the `data` folder at the project root:
# Host: `myproject/data/coder_workspace.db`
# Docker backend volume: `./data:/app/data` (maps host `myproject/data` to container `/app/data`)
# Backend .env: `DATABASE_URL="sqlite:///./data/coder_workspace.db"` (relative to /app in container)
# Alembic (run from `myproject/backend/`): needs `sqlalchemy.url = sqlite:///../data/coder_workspace.db`
# This seems more robust. Let's adjust `config.py` and `alembic.ini` / `env.py` for this.

# For now, let's assume `settings.DATABASE_URL` is correctly configured.
# The path in `settings.DATABASE_URL` is relative to the `backend` directory if it's like `./data/...`
# This is because `config.py` and `.env` are in `backend/`.
# And `main.py` which might call `create_db_and_tables` is also in `backend/`.
# And `alembic` commands are typically run from `backend/`.
# So, `sqlite:///./data/coder_workspace.db` in `backend/.env` means `backend/data/coder_workspace.db`.
# The docker-compose maps `project_root/data` to `/app/data`.
# This is a mismatch.

# Let's standardize: DATABASE_URL in .env refers to a path *relative to the project root's `data` directory*.
# So, `DATABASE_URL="sqlite:///data/coder_workspace.db"` (no leading `./`)
# `config.py` needs to build the correct absolute path or path relative to `backend/`
# `backend/.env` has `DATABASE_URL="sqlite:///./data/coder_workspace.db"` -> this points to `backend/data/`
# `docker-compose.yml` maps `../data` (project root `data`) to `/app/data` in container.

# The `DATABASE_URL` from `app.config.settings` should be the source of truth.
# `app.database.SQLALCHEMY_DATABASE_URL` already uses `settings.DATABASE_URL`.
# We need to ensure that `settings.DATABASE_URL` is correct for both Alembic (run from `backend/`)
# and the app (run from `/app` in Docker).

# If `backend/.env` has `DATABASE_URL="sqlite:///./data/coder_workspace.db"`:
#  - For app in Docker (WORKDIR /app): This path becomes `/app/data/coder_workspace.db`.
#    The volume is `../data:/app/data`. This works.
#  - For Alembic run from `backend/` (where .env is): This path is `backend/data/coder_workspace.db`.
# This means they point to the same physical file if the host's `data` dir is `backend/data`.
# This is simpler. So, the `data` directory should be inside `backend/`.
# Let's ensure `docker-compose.yml` reflects this: `volumes: - ./backend/data:/app/data`

# The current `settings.DATABASE_URL` is "sqlite:///./data/coder_workspace.db".
# When running alembic from `backend/`, this URL correctly points to `backend/data/coder_workspace.db`.
# When running the app in Docker (WORKDIR /app), this URL also correctly points to `/app/data/coder_workspace.db`
# because the Dockerfile copies everything into /app, and the volume maps `./data` (from project root) to `/app/data`.
# This implies the `data` dir for SQLite *should* be at the project root.
# Let's verify `backend/app/database.py` and `backend/app/config.py` again.

# `backend/app/config.py` loads `.env` from `backend/.env`.
# `DATABASE_URL` is `sqlite:///./data/coder_workspace.db`.
# In `backend/app/database.py`:
# `db_file_path_relative_to_app` becomes `./data/coder_workspace.db`.
# `db_file_path_in_container` becomes `/app/data/coder_workspace.db`.
# `db_dir_in_container` becomes `/app/data`. This directory is created if not exists.
# This is for the app running in Docker. This is correct.

# For Alembic, run from `backend/`:
# `config.get_main_option("sqlalchemy.url")` will be used.
# We need to set this to `settings.DATABASE_URL`.
# `settings.DATABASE_URL` is `sqlite:///./data/coder_workspace.db`.
# Relative to `backend/`, this is `backend/data/coder_workspace.db`.
# This is good.

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# The target_metadata is your application's Base metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # include_schemas=True, # Set to True if using multiple schemas
        compare_type=True, # Compare column types
        compare_server_default=True # Compare server defaults
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # include_schemas=True, # Set to True if using multiple schemas
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
