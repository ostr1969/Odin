FROM apache/tika:latest-full

USER root

# Install system packages
RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        mysql-client
RUN apt-get install -y \        
        djvulibre-bin \ 
        calibre \
        fbreader 
RUN apt-get install -y  \
    python3-elasticsearch  \
    python3-mysql.connector  \
    python3-flask \
    python3-pip
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python packages


# Optional: create non-root working directory
WORKDIR /app

USER 1000