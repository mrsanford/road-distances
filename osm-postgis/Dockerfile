# Official PostGIS image
FROM postgis/postgis:16-3.4

# Install osm2pgsql + wget
RUN apt-get update && \
    apt-get install -y osm2pgsql wget && \
    rm -rf /var/lib/apt/lists/*

# Set up environment variables for PostgreSQL
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=roads
ENV POSTGRES_DB=gis

# Make a directory for OSM data
RUN mkdir -p /data

# Download Geofabrik PBF. Initialize PostGIS. Import data using osm2pgsql. Keep PostgreSQL running
RUN wget -O /data/virginia-latest.osm.pbf https://download.geofabrik.de/north-america/us/virginia-latest.osm.pbf && \
    echo "Creating PostGIS extension..." && \
    gosu postgres postgres --single gis <<< "CREATE EXTENSION IF NOT EXISTS postgis;" && \
    echo "Importing OSM data into PostGIS..." && \
    gosu postgres osm2pgsql -U postgres -d gis \
      --create --slim -G --hstore --latlong /data/virginia-latest.osm.pbf && \
    echo "OSM import completed."

# Expose PostgreSQL default port
EXPOSE 5432

# Start PostgreSQL in foreground so container stays alive
CMD ["postgres"]
