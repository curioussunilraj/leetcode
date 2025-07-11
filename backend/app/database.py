from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import os

# Construct the absolute path for the SQLite database file
# settings.DATABASE_URL is like "sqlite:///./data/coder_workspace.db"
# The './data/' part is relative to the WORKDIR in Docker, which is /app
# So, the actual path inside the container will be /app/data/coder_workspace.db

# Ensure the directory for the SQLite database exists
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite:///"):
    # Example: "sqlite:///./data/coder_workspace.db"
    db_file_path_relative_to_app = db_url.split("sqlite:///")[1] # "./data/coder_workspace.db"

    # The WORKDIR in Docker is /app.
    # If db_file_path_relative_to_app starts with "./", it's relative to /app.
    # e.g. "./data/coder_workspace.db" -> "/app/data/coder_workspace.db"
    if db_file_path_relative_to_app.startswith("./"):
        db_file_path_in_container = os.path.join("/app", db_file_path_relative_to_app[2:])
    else: # Assume it's already a path like "data/coder_workspace.db" or an absolute path
        if not os.path.isabs(db_file_path_relative_to_app):
             db_file_path_in_container = os.path.join("/app", db_file_path_relative_to_app)
        else:
            db_file_path_in_container = db_file_path_relative_to_app

    # The volume mount in docker-compose.yml is:
    # - ./data:/app/data  (Host's ./data is mapped to Container's /app/data)
    # So, if DATABASE_URL="sqlite:///./data/coder_workspace.db",
    # the file in container is /app/data/coder_workspace.db
    # which corresponds to ./data/coder_workspace.db on the host.

    db_dir_in_container = os.path.dirname(db_file_path_in_container)
    if not os.path.exists(db_dir_in_container):
        os.makedirs(db_dir_in_container, exist_ok=True)
        # print(f"Created database directory: {db_dir_in_container}")

    # The engine needs the path as it's seen from within the container.
    # If DATABASE_URL="sqlite:///./data/coder_workspace.db"
    # create_engine needs "sqlite:////app/data/coder_workspace.db"
    # No, create_engine with relative path "sqlite:///./data/file.db" works correctly if the CWD is /app.
    # Let's stick to the original relative path from .env, as CWD in container is /app.
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
else:
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args are specific to SQLite
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables
def create_db_and_tables():
    # This function should be called once at application startup.
    # For example, in main.py or a startup event.
    # Base.metadata.create_all(bind=engine)
    # We will use Alembic for migrations, so this line might not be needed here
    # but it's useful for initial setup or testing without migrations.
    # For now, let's assume Alembic will handle table creation primarily.
    # However, this function can be useful for initial setup in dev or testing.
    Base.metadata.create_all(bind=engine)
    print("create_db_and_tables called: Base.metadata.create_all(bind=engine) executed.")


if __name__ == "__main__":
    print(f"Database URL: {SQLALCHEMY_DATABASE_URL}")
    # To test creation, you would import models and then call:
    # from .models import Problem, Submission # Make sure models are defined
    # Base.metadata.create_all(bind=engine)
    # print("Database tables created (if models are defined and imported).")

    # Test directory creation logic
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite:///"):
        path_part = SQLALCHEMY_DATABASE_URL.split("sqlite:///")[1]
        if path_part.startswith("./"): # e.g., ./data/file.db
            # Relative to WORKDIR /app
            abs_path = os.path.abspath(os.path.join("/app", path_part[2:]))
        elif not os.path.isabs(path_part): # e.g., data/file.db
            abs_path = os.path.abspath(os.path.join("/app", path_part))
        else: # e.g., /somewhere/file.db
            abs_path = path_part

        db_dir = os.path.dirname(abs_path)
        print(f"Expected DB directory in container: {db_dir}")
        # This will try to create it on the machine running this script if not in Docker.
        # if not os.path.exists(db_dir):
        #     os.makedirs(db_dir, exist_ok=True)
        #     print(f"Created directory {db_dir} (if run locally)")
        # else:
        #     print(f"Directory {db_dir} already exists (if run locally)")
    print("SQLAlchemy engine and SessionLocal configured.")
