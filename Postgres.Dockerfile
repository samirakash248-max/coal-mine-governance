FROM postgis/postgis:15-3.3-alpine

RUN apk add --no-cache \
    postgresql15-dev \
    build-base \
    git \
    clang15 \
    llvm15

RUN git clone --branch v0.8.6 --depth 1 https://github.com/pgvector/pgvector.git /tmp/pgvector \
    && cd /tmp/pgvector \
    && make \
    && make install \
    && rm -rf /tmp/pgvector \
    && apk del build-base git clang15 llvm15
