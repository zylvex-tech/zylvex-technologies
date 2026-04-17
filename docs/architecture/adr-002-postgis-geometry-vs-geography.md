# ADR-002: PostGIS Geometry vs Geography for Anchor Locations

## Status: ✅ Resolved

## Context
Spatial Canvas needs to store GPS coordinates and query anchors within a given radius.

## Original Decision (now superseded)
The Anchor.location column originally used `Geometry('POINT', srid=4326)` (Cartesian coordinate system).
Distance radius queries used a degree approximation: radius_km / 111.0.
This caused ~50% error at 60°N latitude.

## Resolution
Migrated to `Geography('POINT', srid=4326)` for meter-accurate queries at all latitudes.

**Changes made:**
- `Anchor.location` column type changed from `Geometry` to `Geography` in the model
- `ST_DWithin` now uses meters: `radius_km * 1000`
- Alembic migration `003_geography_media` handles data migration:
  1. Adds `location_geo` Geography column
  2. Copies data via `location::geography`
  3. Drops old Geometry column, renames new one
  4. Recreates GIST spatial index
- API accepts `radius_km` as float, converts to meters internally
- All tests updated for meter-based radius assertions

## Consequences
+ Accurate distance calculations at all latitudes (no degree approximation)
+ ST_DWithin uses meters directly — no conversion errors
+ Same GIST index performance
- Slightly more storage per row (Geography vs Geometry)
