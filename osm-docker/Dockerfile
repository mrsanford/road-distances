# Using official PostGIS image for base
FROM postgis/postgis:16-3.4

# Install osm2pgsql and wget
RUN apt-get update && \
    apt-get install -y osm2pgsql wget && \
    rm -rf /var/lib/apt/lists/*

# PostgreSQL environment variables
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=roads
ENV POSTGRES_DB=gis

# OSM data copy for the image
COPY virginia-latest.osm.pbf /data/virginia.osm.pbf

# Initialization script for first-time DB creation
COPY init_osm.sh /docker-entrypoint-initdb.d/init_osm.sh
RUN chmod +x /docker-entrypoint-initdb.d/init_osm.sh

# Expose port for database connection
EXPOSE 5432
