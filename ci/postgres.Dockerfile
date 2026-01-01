FROM postgres:17.2-alpine

ENV PG_PARTMAN_VERSION=v5.2.4

# Install dependencies and build pg_partman in a single layer
RUN set -ex \
    \
    && apk add --no-cache --virtual .fetch-deps \
        ca-certificates \
        openssl \
        tar \
        wget \
    \
    && apk add --no-cache --virtual .build-deps \
        autoconf \
        automake \
        g++ \
        clang19 \
        llvm19 \
        libtool \
        libxml2-dev \
        make \
        perl \
        postgresql17-dev \
    \
    && wget -O pg_partman.tar.gz "https://github.com/pgpartman/pg_partman/archive/$PG_PARTMAN_VERSION.tar.gz" \
    && mkdir -p /usr/src/pg_partman \
    && tar \
        --extract \
        --file pg_partman.tar.gz \
        --directory /usr/src/pg_partman \
        --strip-components 1 \
    && rm pg_partman.tar.gz \
    && cd /usr/src/pg_partman \
    && make \
    && make install \
    && cd / \
    && rm -rf /usr/src/pg_partman \
    && apk del .fetch-deps .build-deps \
    && rm -rf /var/cache/apk/*

# Production-ready PostgreSQL configuration
# These can be overridden via environment variables or custom postgresql.conf
ENV POSTGRES_INITDB_ARGS="--encoding=UTF8 --locale=C"

# Copy custom postgresql.conf if needed
# Usage: COPY postgresql.conf /etc/postgresql/postgresql.conf
# Or mount it: docker run -v /path/to/postgresql.conf:/etc/postgresql/postgresql.conf

# Install monitoring extensions (optional, but recommended for production)
# pg_stat_statements - tracks execution statistics of all SQL statements
# pg_buffercache - shows what's in the shared buffer cache
# These are built-in extensions, just need to be enabled in postgresql.conf
