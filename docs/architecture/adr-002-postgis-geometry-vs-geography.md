# ADR-002: PostGIS Geometry vs Geography for Anchor Locations

## Status: Accepted with known limitation

## Context
Spatial Canvas needs to store GPS coordinates and query anchors within a given radius.

## Decision
The Anchor.location column uses `Geometry('POINT', srid=4326)` (Cartesian coordinate system).
Distance radius queries use a degree approximation: radius_km / 111.0.

## Consequences
+ Simpler setup; GiST index works out of the box
- ~0.6% error at equator, up to ~50% error at 60°N latitude for radius calculations
- Inaccuracy grows significantly at high latitudes

## Future improvement
Migrate to `Geography('POINT', srid=4326)` for meter-accurate queries. Requires an Alembic
migration to change the column type. ST_DWithin on Geography uses meters directly.
