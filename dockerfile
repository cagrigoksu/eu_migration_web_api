FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    make \
    libssl-dev \
    libffi-dev \
    python3-dev \
    sqlcipher \
    libsqlcipher-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy project files to the container
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip \
    && CFLAGS="-I/usr/include -DSQLITE_HAS_CODEC" LDFLAGS="-lcrypto -lsqlcipher" pip install --no-cache-dir -r requirements.txt \
    && apt-get remove --purge -y gcc python3-dev build-essential \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Expose the port the app runs on
EXPOSE 8080

# Command to run the Flask application
CMD ["python", "app.py"]
