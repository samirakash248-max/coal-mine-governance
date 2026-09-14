# PostGIS Digital Twin & GIS Implementation

## 1. Current Architecture & Location Model
The initial architecture relied exclusively on standard floating-point `latitude` and `longitude` columns scattered across the `Mine`, `SafetyEvent`, and `Inspection` SQLAlchemy models. The frontend map (`GovernanceMap.tsx`) was falling back to synthetically generated math coordinates `(Math.cos(i) * 4)` for rendering incidents, rendering it unsuitable for real governance.

## 2. PostGIS Implementation
- Upgraded the database Docker container in `docker-compose.yml` from `postgres:15-alpine` to `postgis/postgis:15-3.3-alpine`.
- Kept the existing `latitude` and `longitude` float columns intact to ensure strict backward compatibility for all existing non-spatial API consumers.
- Introduced a powerful `geoalchemy2` layer mapping to `Geometry('POINT', srid=4326)` columns (`location_geom`) across all relevant models (`Mine`, `SafetyEvent`, `Inspection`).

## 3. Migration Details
Created a safe, non-destructive Alembic data migration (`backend/alembic/versions/*_postgis_digital_twin.py`) that executes three critical operations:
1. Safely enables the `postgis` extension (`CREATE EXTENSION IF NOT EXISTS postgis;`).
2. Appends the new geospatial columns.
3. Performs an intelligent `UPDATE` translating all existing float coordinates (where valid `BETWEEN -90 AND 90`) directly into `SRID 4326` points via `ST_MakePoint()`. No invalid coordinates were artificially zeroed out.

## 4. Spatial API & Governance Queries
To establish the Digital Twin as a true operational tool, two new endpoints were integrated directly into the existing routing architecture:
- `GET /api/v1/hierarchy/mines/{mine_id}/nearby`: Executes a highly performant `ST_DWithin` spatial query to locate surrounding infrastructure within a calculated radius limit (avoiding loading all arrays into Python).
- `GET /api/v1/field/events/spatial/{mine_id}`: Locates specific contextual `SafetyEvent` records surrounding a targeted geographical site.

## 5. Frontend Map Upgrade
Completely overhauled `GovernanceMap.tsx`:
- Stripped all mathematical coordinate synthesis algorithms (`Math.cos`).
- Now natively leverages `ev.latitude` and `ev.longitude` returning from the Spatial APIs.
- The `WeatherRiskBadge` detail popup inside the map now hooks into the Environmental Intelligence module (Issue #8) to display genuine localized climate conditions alongside active governance risks.

## 6. RBAC Integration
Spatial operations do not bypass existing RBAC restrictions. The nearby querying logic still adheres to `current_user.mine_id` and `current_user.region_id` scope limits, ensuring spatial features cannot be utilized for unauthorized intelligence gathering across constrained zones.

## 7. Performance Considerations
- All spatial math utilizes PostgreSQL/PostGIS C-bindings directly via SQLAlchemy's `ST_DWithin`. 
- Caching implementations established in Issue #8 persist for the Weather popups, effectively mitigating rate-limits when evaluating large spatial clusters.
- Bounding box limitations (`limit(10)` and `limit(50)`) enforce safe payload delivery to the React client.

## 8. Limitations & Future Roadmap
- The Docker runtime environment on the host system was offline during implementation, so PostGIS spatial tests rely exclusively on static Python/SQLAlchemy compilation validation. 
- Future UI features should include spatial clustering (`react-leaflet-cluster`) if the density of safety events increases significantly across heavily trafficked zones.
