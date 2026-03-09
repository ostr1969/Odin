FROM apache/tika:latest-full

USER root
#docker build -t tika:flask .
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
RUN apt-get install -y git jq  
RUN apt-get install -y  python3-pip      python-is-python3   iproute2 iputils-ping vim 
RUN apt-get install -y unzip p7zip-full
RUN python3 -m venv /opt/venv 
ENV PATH="/opt/venv/bin:$PATH"
RUN  /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir elasticsearch mysql-connector-python flask
RUN python3 -m pip install --no-cache-dir mobi html2text requests shutils
RUN pip3 install torch --no-cache-dir --index-url https://download.pytorch.org/whl/cpu
RUN python3 -m pip install --no-cache-dir sentence-transformers
RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/python /usr/local/bin/python 
# Upgrade pip and install Python packages
RUN python3 -m pip install --no-cache-dir rapidfuzz

# Optional: create non-root working directory
WORKDIR /app

USER 1000