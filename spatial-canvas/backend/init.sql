-- Create spatial_canvas database if not exists
SELECT 'CREATE DATABASE spatial_canvas'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'spatial_canvas')\gexec

-- Create auth_service database if not exists
SELECT 'CREATE DATABASE auth_service'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'auth_service')\gexec

-- Enable PostGIS extension for spatial_canvas
\c spatial_canvas
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Enable PostGIS extension for auth_service
\c auth_service
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
