FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    make \
    libssl-dev \
    libffi-dev \
    libsqlite3-dev \
    python3-dev \
    sqlcipher \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy project files to the container
COPY . /app

# Add SQLCipher dependencies before pip install
RUN apt-get update && apt-get install -y \
    libsqlcipher-dev \
    gcc \
    python3-dev \
    build-essential \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove --purge -y gcc python3-dev build-essential \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Expose the port the app runs on
EXPOSE 8080

# Command to run the Flask application
CMD ["python", "app.py"]
