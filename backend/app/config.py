import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from functools import lru_cache

# Load .env file from the backend directory if it exists
# The working directory for the backend service in docker-compose is /app
# So, .env should be in /app/.env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=dotenv_path)

class Settings(BaseSettings):
    GEMINI_API_KEY: str = "YOUR_GEMINI_API_KEY_HERE" # Default if not in .env
    DATABASE_URL: str = "sqlite:///./data/coder_workspace.db" # Default if not in .env

    DOCKER_TIMEOUT_SECONDS: int = 10
    DOCKER_MEMORY_LIMIT_MB: int = 256

    DOCKER_BASE_IMAGE_PYTHON: str = "python:3.11-slim"
    DOCKER_BASE_IMAGE_JAVASCRIPT: str = "node:18-slim"
    DOCKER_BASE_IMAGE_CPP: str = "gcc:latest"

    # WORKSPACE_DIR_CONTAINER is relative to the /app directory inside the container
    WORKSPACE_DIR_CONTAINER: str = "/app/workspace_temp"

    PYTHON_EXECUTION_FILENAME: str = "solution.py"
    JAVASCRIPT_EXECUTION_FILENAME: str = "solution.js"
    CPP_EXECUTION_FILENAME: str = "solution.cpp"
    CPP_COMPILED_FILENAME: str = "solution_exec"

    LOG_LEVEL: str = "INFO"

    # Allow configuring these via environment variables
    class Config:
        env_file = ".env" # Specifies that Pydantic should load from .env
        env_file_encoding = 'utf-8'
        extra = 'ignore' # Ignore extra fields from .env

@lru_cache()
def get_settings() -> Settings:
    # Check if .env exists and load it
    # This path is relative to where config.py is located.
    # So, ../.env means one level up from 'app' directory, i.e., 'backend/.env'
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        # print(f"Loading .env file from: {env_path}")
        return Settings(_env_file=env_path, _env_file_encoding='utf-8')
    # print("No .env file found, using default settings or environment variables.")
    return Settings()

settings = get_settings()

# To ensure the WORKSPACE_DIR_CONTAINER is an absolute path within the container context
if not os.path.isabs(settings.WORKSPACE_DIR_CONTAINER) and settings.WORKSPACE_DIR_CONTAINER.startswith("/app"):
    # This means it's already correctly set as an absolute path from the container's perspective
    pass
elif not os.path.isabs(settings.WORKSPACE_DIR_CONTAINER):
    # If it's a relative path like "workspace_temp", make it absolute from /app
    settings.WORKSPACE_DIR_CONTAINER = os.path.join("/app", settings.WORKSPACE_DIR_CONTAINER)


if __name__ == "__main__":
    # For testing if settings are loaded correctly
    print(f"Gemini API Key: {settings.GEMINI_API_KEY}")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Workspace Dir: {settings.WORKSPACE_DIR_CONTAINER}")
    # Create the workspace directory if it doesn't exist (useful for local dev outside Docker)
    # Note: Inside Docker, this path is relative to /app, which is the WORKDIR.
    # For local testing of this script, it might create it in backend/app/workspace_temp

    # Correct path for local testing of config.py (relative to backend/ not backend/app/)
    local_workspace_path_for_testing = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.path.basename(settings.WORKSPACE_DIR_CONTAINER))

    # if not os.path.exists(local_workspace_path_for_testing):
    #     os.makedirs(local_workspace_path_for_testing)
    # print(f"Workspace directory for local test: {local_workspace_path_for_testing} (created if not exists)")
    print(f"Python base image: {settings.DOCKER_BASE_IMAGE_PYTHON}")
    print(f"JS base image: {settings.DOCKER_BASE_IMAGE_JAVASCRIPT}")
    print(f"C++ base image: {settings.DOCKER_BASE_IMAGE_CPP}")
    print(f"Python exec filename: {settings.PYTHON_EXECUTION_FILENAME}")
    print(f"JS exec filename: {settings.JAVASCRIPT_EXECUTION_FILENAME}")
    print(f"C++ exec filename: {settings.CPP_EXECUTION_FILENAME}")
    print(f"C++ compiled filename: {settings.CPP_COMPILED_FILENAME}")
