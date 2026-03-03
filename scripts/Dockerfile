FROM apache/tika:latest-full

USER root
RUN apt-get update && \
    apt-get install -y djvulibre-bin calibre fbreader && \
    apt-get clean

USER 1000