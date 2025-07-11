# Stage 1: Build stage (if needed, e.g., for compiled languages or complex setups)
# For Python, it's often simpler to do it in one stage unless you have specific needs.

# Stage 2: Final stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies (if any)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     # any system packages needed, e.g., build-essential for some Python packages
#  && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# Use reload for development, but not for production.
# The docker-compose.yml will manage the command and can enable reload if needed.
# For now, this is a good default.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
