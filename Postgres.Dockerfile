FROM postgis/postgis:16-3.4

RUN apt-get update \
    && apt-cache showpkg postgresql-16-pgvector \
    && apt-get install -y --no-install-recommends \
       postgresql-16-pgvector \
    && rm -rf /var/lib/apt/lists/*
